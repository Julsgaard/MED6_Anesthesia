import asyncio
import cv2
import numpy as np
import time
from library import functions

host = '0.0.0.0'
port = 5000


async def handle_client(reader, writer, image_queue, tilt_queue):
    """Handles the client connection reads the image data and saves it to a file. The image filename is then put in
    the server_image_queue."""

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
        difficultyOfIntubation = int.from_bytes(difficulty_data, 'big')

        # Weight in kg
        # Difficulty of Intubation: 0 = No, 1 = Yes
        print(f"Received - Weight: {weight}, Difficulty of Intubation: {difficultyOfIntubation}")

        while True:
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

                # Create a filename for the image
                image_filename = f"{functions.session_path}/received_image_{image_counter}.jpeg"

                # Save the corrected image to a file
                cv2.imwrite(image_filename, corrected_image)

                # Put the image filename in the server_image_queue
                image_queue.put(image_filename)

                # Increment the image counter
                image_counter += 1

                # Prints the FPS
                frame_counter, prev_time = fps_counter(frame_counter, prev_time)

            else:
                print("No more data from client.")
                break

    except asyncio.IncompleteReadError:
        print(f"Client disconnected: {client_addr}")
    finally:
        writer.close()
        await writer.wait_closed()


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


def fps_counter(frame_counter, prev_time):
    """Calculates and print the FPS every second"""

    # Increment frame counter
    frame_counter += 1
    # Calculate FPS every second
    curr_time = time.time()
    if curr_time - prev_time >= 1:
        fps = frame_counter / (curr_time - prev_time)
        print(f"FPS: {fps}")
        # print(f"Image ByteSize: {size}")
        frame_counter = 0
        prev_time = curr_time
    return frame_counter, prev_time


async def async_server(image_queue, tilt_queue):
    """Starts the server and listens for incoming connections"""

    server = await asyncio.start_server(lambda r, w: handle_client(r, w, image_queue, tilt_queue), host, port)
    sock_name = server.sockets[0].getsockname()
    print(f"Starting server on {sock_name}")
    async with server:
        await server.serve_forever()


def start_server(image_queue, tilt_queue):
    asyncio.run(async_server(image_queue, tilt_queue))
