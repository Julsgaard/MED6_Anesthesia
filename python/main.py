from library import server, functions, newburgers_main
import threading
import queue

host_ip = '0.0.0.0'
server_port = 5000

image_queue = queue.Queue()


if __name__ == '__main__':
    functions.check_for_logs_folder()
    functions.delete_empty_folders_in_logs()
    functions.create_session_folder()

    print("Server starting...")

    # Starts the server in a new thread
    server_thread = threading.Thread(target=server.start_server, args=(host_ip, server_port, image_queue))
    server_thread.start()


while True:
    # Get the image path from the queue
    image_path = image_queue.get()
    print(f"Image queue size: {image_queue.qsize()}")
    print(f"Processing image: {image_path}")



