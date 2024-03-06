import os
from datetime import datetime
import cv2 as cv
import threading
import queue

# Directory where images from the phone will be saved
logs_folder = 'logs/phone_images'

# Directory where the images from the phone will be saved
session_folder = datetime.now().strftime('%d-%b-%Y_%H-%M-%S')
session_path = os.path.join(logs_folder, session_folder)


# Creates a new logs folder if it doesn't exist
def check_for_logs_folder():
    if not os.path.exists(logs_folder):
        print(f"Creating folder: {logs_folder}")
        os.makedirs(logs_folder)


# Creates a new session folder
def create_session_folder():
    if not os.path.exists(session_path):
        print(f"Creating folder: {session_path}")
        os.makedirs(session_path)


# Deletes empty folders in the logs folder
def delete_empty_folders_in_logs():
    for folder_path, folder_name, files in os.walk(logs_folder):
        if not folder_name and not files:
            os.rmdir(folder_path)
            print(f"Deleted empty directory: {folder_path}")


def start_display_thread(display_image_queue):
    print("Starting display thread...")
    display_thread = threading.Thread(target=display_images, args=(display_image_queue,))
    display_thread.start()


def display_images(display_image_queue):
    while True:
        # Get the current image from the queue
        current_image = display_image_queue.get()

        # print(f"Displaying image: {current_image}")
        # Read the image from the provided path
        # image = cv.imread(current_image)

        # Display the image
        cv.imshow('Live Image', current_image)

        # Break the loop if 'q' is pressed
        if cv.waitKey(10) & 0xFF == ord('q'):
            break

    # Close the OpenCV window
    cv.destroyAllWindows()
