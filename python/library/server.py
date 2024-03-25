import asyncio
import queue
import cv2
import numpy as np
import os
import time

host = '0.0.0.0'
port = 5000

# Ensure the directory for saving images exists
images_dir = "received_images"
os.makedirs(images_dir, exist_ok=True)


async def handle_client(reader, writer, image_queue, tilt_queue):
    image_counter = 0
    prev_time = time.time()  # Initialize prev_time
    frame_counter = 0  # Initialize frame counter

    try:
        while True:
            # TODO: Dynamic resolution in separate function?
            # Read the resolution data first
            resolution_data = await reader.readexactly(8)
            width = int.from_bytes(resolution_data[:4], 'big')
            height = int.from_bytes(resolution_data[4:], 'big')

            # Then read the size of the image data
            size_data = await reader.readexactly(4)
            size = int.from_bytes(size_data, 'big')

            if size:
                image_data = await reader.readexactly(size)
                # print(f"Received data of size: {size} for resolution: {width}x{height}")

                if size == width * height:  # Check if data size matches the resolution
                    image = np.frombuffer(image_data, dtype=np.uint8).reshape((height, width))

                    image_filename = f"{images_dir}/received_image_{image_counter}.jpg"

                    # Save the image to a file
                    cv2.imwrite(image_filename, image) #TODO: Maybe don't save it during runtime - Depends on how we use the images in the code

                    # Put the image filename in the server_image_queue
                    image_queue.put(image_filename)

                    # print(f"Image saved to {image_filename}")
                    image_counter += 1

                    # Display the image
                    # cv2.imshow('Received Image', image)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                else:
                    print("Mismatched data size, cannot form an image.")

                # Increment frame counter
                frame_counter += 1

                # TODO: Calculate FPS in separate function
                # Calculate FPS every second
                curr_time = time.time()
                if curr_time - prev_time >= 1:
                    fps = frame_counter / (curr_time - prev_time)
                    print(f"FPS: {fps}")
                    frame_counter = 0
                    prev_time = curr_time

                    print(f"Received data of size: {size} for resolution: {width}x{height}")

            else:
                print("No more data from client.")
                break

    except asyncio.IncompleteReadError:
        print("Client disconnected.")

    # TODO: Maybe the server can connect to the client again after the client disconnects?
    finally:
        writer.close()
        await writer.wait_closed()


async def async_server(image_queue, tilt_queue):
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, image_queue, tilt_queue), host, port)
    sock_name = server.sockets[0].getsockname()
    print(f"Starting server on {sock_name}")
    async with server:
        await server.serve_forever()


def start_server(image_queue, tilt_queue):
    asyncio.run(async_server(image_queue, tilt_queue))


if __name__ == '__main__':
    start_server(image_queue=queue.Queue, tilt_queue=None)
