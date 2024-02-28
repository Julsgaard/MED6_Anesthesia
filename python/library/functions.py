import os
from datetime import datetime

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
