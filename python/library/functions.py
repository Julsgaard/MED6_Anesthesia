import os
from datetime import datetime
import cv2 as cv
import threading
import numpy as np
import torch


# Directory where images from the phone will be saved
logs_folder = 'logs'


# Creates a new logs folder if it doesn't exist
def check_for_logs_folder():
    if not os.path.exists(logs_folder):
        print(f"Creating folder: {logs_folder}")
        os.makedirs(logs_folder)


# Creates a new session folder
def create_session_folder():
    # Directory where the images from the phone will be saved
    session_folder = datetime.now().strftime('%d-%b-%Y_%H-%M-%S')
    session_path = os.path.join(logs_folder, session_folder)

    print(f"Creating folder: {session_path}")
    os.makedirs(session_path)

    return session_path  # Return the session_path


# Deletes empty folders in the logs folder
def delete_empty_folders_in_logs():
    for entry in os.scandir(logs_folder):
        if entry.is_dir(follow_symlinks=False):
            if not os.listdir(entry.path):  # Check if directory is empty
                os.rmdir(entry.path)
                print(f"Deleted empty directory: {entry.path}")


def start_display_thread(display_image_queue):
    print("Starting display thread...")
    display_thread = threading.Thread(target=display_images, args=(display_image_queue,))
    display_thread.start()


def display_images(display_image_queue):
    while True:
        # Get the current image from the queue
        current_image = display_image_queue.get()
        #print(f"Displaying image: {current_image}")

        # Check if current_image is a string (indicating it's a path)
        if isinstance(current_image, str):
            # Read the image from the provided path
            image = cv.imread(current_image)
        elif isinstance(current_image, np.ndarray):
            # current_image is an actual image
            image = current_image
        else:
            print("Invalid image or image path provided.")
            continue

        # Display the image
        cv.imshow('Live Image', image)

        # Break the loop if 'q' is pressed
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the OpenCV window
    cv.destroyAllWindows()


# Function to display the predicted images
def imshow_cv(inp, title=None):
    if isinstance(inp, torch.Tensor):
        inp = inp.numpy().transpose((1, 2, 0))

    # Reverse the normalization
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = inp * std + mean  # First reverse the normalization
    inp = np.clip(inp, 0, 1)  # Then clip to the range [0, 1]

    # Convert it to [0, 255] for display
    inp = (inp * 255).astype(np.uint8)

    # Display the image
    cv.imshow(title if title else 'Image', inp)
    cv.waitKey(0)  # Wait for a key press to proceed
    cv.destroyAllWindows()  # Close the window after key press


def find_state_for_image_path(image_path):
    #print(f"Image path: {image_path}")  # Debugging line

    # Extract the base directory or folder name from the image path
    base_directory = os.path.basename(os.path.dirname(image_path))

    # print(f"Base directory: {base_directory}")  # Debugging line


    # Define actions based on directory names
    if base_directory.lower() == 'mallampati':
        return "Mallampati"
    elif base_directory.lower() == 'mouth opening':
        return "Mouth Opening"
    elif base_directory.lower() == 'neck movement':
        return "Neck Movement"
    else:
        return "Unknown category"

