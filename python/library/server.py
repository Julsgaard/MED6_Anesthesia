import asyncio
import json
import os
import cv2
import numpy as np
import time
from library import functions

host = '0.0.0.0'
port = 5000


async def handle_client(reader, writer, image_queue, tilt_queue, eye_level_queue):
    """Handles the client connection reads the image data and saves it to a file. The image filename is then put in
    the server_image_queue."""

    session_path = functions.create_session_folder()  # Create a new session folder when a client connects

    image_counter = 0
    prev_time = time.time()  # Initialize prev_time
    frame_counter = 0  # Initialize frame counter

    client_addr = writer.get_extra_info('peername')
    print(f"Client connected: {client_addr}")

    try:
        # Read the weight (4 bytes)
        weight_data = await reader.readexactly(4)
        weight = int.from_bytes(weight_data, 'big')

        # Read the difficulty of intubation (1 byte)
        difficulty_data = await reader.readexactly(1)
        difficulty_of_intubation = int.from_bytes(difficulty_data, 'big')

        # Convert the difficulty of intubation to a string
        if difficulty_of_intubation == 0:
            difficulty_of_intubation = "No difficulty"
        if difficulty_of_intubation == 1:
            difficulty_of_intubation = "Definite difficulty"

        # Save the weight and difficulty of intubation to the session folder
        with open(f"{session_path}/weight and difficulty.txt", 'w') as f:
            f.write(f"Weight: {weight}\n")
            f.write(f"Difficulty of Intubation: {difficulty_of_intubation}\n")

        # Weight in kg
        # Difficulty of Intubation: 0 = No, 1 = Yes
        print(f"Received - Weight: {weight}, Difficulty of Intubation: {difficulty_of_intubation}")

        while True:

            current_state_data = await reader.readexactly(4)
            current_state = int.from_bytes(current_state_data, 'big')

            if current_state == 0:  # Mouth Opening state
                current_state = 'Mouth Opening'

                image_counter, lux_value, tilt_angle = await video_stream(reader, image_queue, session_path,
                                                                          current_state, image_counter)

                eye_level = eye_level_queue.get()  # Get the eye level from the queue

                send_data = {
                    "eye_level": eye_level,  # TODO: Change to eye level
                    "test": "test"
                }

                # Send data to the client
                await send_to_client(send_data, writer)

            elif current_state == 1:  # Mallampati state
                current_state = 'Mallampati'

                image_counter, lux_value, tilt_angle = await video_stream(reader, image_queue, session_path,
                                                                          current_state, image_counter)

                eye_level = eye_level_queue.get()  # Get the eye level from the queue

                send_data = {
                    "eye_level": eye_level,  # TODO: Change to eye level
                    "test": "test"
                }

                # Send data to the client
                await send_to_client(send_data, writer)

            elif current_state == 2:  # Neck Movement state
                current_state = 'Neck Movement'

                image_counter, lux_value, tilt_angle = await video_stream(reader, image_queue, session_path,
                                                                          current_state, image_counter)

                # eye_level = eye_level_queue.get()  # Get the eye level from the queue (To clear the queue)

                send_data = {
                    "test": "test"
                }

                # Send data to the client
                await send_to_client(send_data, writer)

            else:
                print("Unknown state closing connection")
                break

            # Prints the FPS, current state, lux value, and tilt angle every second
            frame_counter, prev_time = print_every_x(
                frame_counter,
                prev_time,
                current_state,
                lux_value,
                tilt_angle,
                print_time=1  # Prints every second
            )

    except asyncio.IncompleteReadError:
        print(f"Client disconnected: {client_addr}")
    except ConnectionResetError:
        print(f"Connection reset by client: {client_addr}")
    finally:
        writer.close()
        await writer.wait_closed()


async def send_to_client(send_data, writer):
    message = json.dumps(send_data)
    # print(f"Sending: {message}")

    writer.write(message.encode())

    await writer.drain()


async def video_stream(reader, image_queue, session_path, current_state, image_counter):
    # Read the size of the image data
    size_data = await reader.readexactly(4)
    size = int.from_bytes(size_data, 'big')

    # Read the resolution of the image
    resolution_data = await reader.readexactly(8)
    width = int.from_bytes(resolution_data[:4], 'big')
    height = int.from_bytes(resolution_data[4:], 'big')

    if size:
        # Read the image data
        image_data = await reader.readexactly(size)

        yuv_image = convert_nv12_to_bgr(height, image_data, width)

        # Rotate the image counter-clockwise 90 degrees to correct the orientation
        corrected_image = cv2.rotate(yuv_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Create a directory for the state if it doesn't exist
        state_dir = f"{session_path}/{current_state}"
        os.makedirs(state_dir, exist_ok=True)

        # Read the brightness value
        lux_value = await reader.readexactly(4)
        lux_value = int.from_bytes(lux_value, 'big')  # Convert the byte string to an integer
        # print(f"Lux Value: {lux_value}")

        # Read the tilt angle
        tilt_angle = await reader.readexactly(4)
        tilt_angle = int.from_bytes(tilt_angle, 'big')  # Convert the byte string to an integer
        # print(f"Tilt Angle: {tilt_angle}")

        # Create the image filename
        image_filename = f"{state_dir}/{image_counter}image_{lux_value}lux_{tilt_angle}angle.jpeg"

        # Save the corrected image to a file
        cv2.imwrite(image_filename, corrected_image)

        # Put the image filename in the server_image_queue
        image_queue.put(image_filename)

        # Increment the image counter
        image_counter += 1

        return image_counter, lux_value, tilt_angle

    else:
        print("No more data from client.")


def convert_nv12_to_bgr(height, image_data, width):
    """Converts NV12 image data to BGR format for OpenCV."""

    # NV21 has the Y plane followed by the UV plane (which is half the size of Y)
    y_plane_len = width * height
    uv_plane_len = width * height // 2  # UV plane has half the number of pixels
    y_plane = np.frombuffer(image_data[:y_plane_len], dtype=np.uint8).reshape((height, width))

    # If there's a byte missing in the UV plane, add a neutral (zero) byte
    if len(image_data[y_plane_len:]) == uv_plane_len - 1:
        uv_data = image_data[y_plane_len:] + b'\x00'  # Append a single neutral byte
    else:
        uv_data = image_data[y_plane_len:y_plane_len + uv_plane_len]
    uv_plane = np.frombuffer(uv_data, dtype=np.uint8).reshape((height // 2, width // 2, 2))

    # Convert NV21 to BGR format for OpenCV
    yuv_image = cv2.cvtColorTwoPlane(y_plane, uv_plane, cv2.COLOR_YUV2BGR_NV12)

    return yuv_image


def print_every_x(frame_counter, prev_time, current_state, lux_value, tilt_angle, print_time=1):
    """Prints values every x"""

    # Increment frame counter
    frame_counter += 1
    # Calculate FPS every second
    curr_time = time.time()
    if curr_time - prev_time >= print_time:
        fps = frame_counter / (curr_time - prev_time)
        print("=================================")
        print(f"Current State: {current_state}")
        print(f"FPS: {fps}")
        print(f"Lux Value: {lux_value}")
        print(f"Tilt Angle: {tilt_angle}")
        # print(f"Image ByteSize: {size}")
        frame_counter = 0
        prev_time = curr_time
    return frame_counter, prev_time


async def async_server(image_queue, tilt_queue, eye_level_queue):
    """Starts the server and listens for incoming connections"""

    server = await asyncio.start_server(lambda r, w: handle_client(r, w, image_queue, tilt_queue, eye_level_queue),
                                        host, port)
    sock_name = server.sockets[0].getsockname()
    print(f"Starting server on {sock_name}")
    async with server:
        await server.serve_forever()


def start_server(image_queue, tilt_queue, eye_level_queue):
    asyncio.run(async_server(image_queue, tilt_queue, eye_level_queue))
