from flask import Flask, request, jsonify
import os
import threading
import cv2 as cv
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Directory where images from the phone will be saved
UPLOAD_FOLDER = 'logs/phone_images'

# Shared resource for the latest image
latest_image = None
lock = threading.Lock()

# TODO: Needs to be cleaned up + comments
# TODO: Move server to another script and folder functions

def display_images():
    global latest_image
    while True:
        with lock:
            if latest_image is not None:
                cv.imshow('Live Image', latest_image)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
    cv.destroyAllWindows()


@app.route('/upload', methods=['POST'])
def upload_file():
    global latest_image
    if 'picture' in request.files:
        file = request.files['picture']
        filename = file.filename
        filename = secure_filename(filename)

        temp_path = os.path.join(SESSION_PATH, filename)
        file.save(temp_path)

        # Update the latest image
        with lock:
            latest_image = cv.imread(temp_path)

        return jsonify(message="Image received and updated successfully!")
    else:
        return jsonify(message="No image received"), 400


def delete_empty_directories(path):
    for dirpath, dirnames, files in os.walk(path):
        if not dirnames and not files:
            os.rmdir(dirpath)
            print(f"Deleted empty directory: {dirpath}")


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"Creating directory: {UPLOAD_FOLDER}")
        os.makedirs(UPLOAD_FOLDER)

    delete_empty_directories(UPLOAD_FOLDER)

    # Create a new directory for the current session
    session_folder = datetime.now().strftime('%d-%b-%Y_%H-%M-%S')
    SESSION_PATH = os.path.join(UPLOAD_FOLDER, session_folder)
    if not os.path.exists(SESSION_PATH) and not app.debug:
        print(f"Creating directory: {SESSION_PATH}")
        os.makedirs(SESSION_PATH)

    display_thread = threading.Thread(target=display_images)
    display_thread.start()
    print("Server starting...")
    app.run(debug=False, host='0.0.0.0', port=5000)
    print("Server stopped.")
