import os
import cv2 as cv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from library import functions
import threading


app = Flask(__name__)

latest_image = None
lock = threading.Lock()


@app.route('/upload', methods=['POST'])
def upload_file():
    global latest_image
    if 'picture' in request.files:
        file = request.files['picture']
        filename = file.filename
        filename = secure_filename(filename)

        temp_path = os.path.join(functions.session_path, filename)
        file.save(temp_path)

        with lock:
            latest_image = cv.imread(temp_path)

        return jsonify(message="Image received and updated successfully!")
    else:
        return jsonify(message="No image received"), 400


def start_server(host_ip, server_port):
    app.run(debug=False, host=host_ip, port=server_port)


def display_images():
    global latest_image
    while True:
        with lock:
            if latest_image is not None:
                cv.imshow('Live Image', latest_image)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
    cv.destroyAllWindows()


display_thread = threading.Thread(target=display_images)
# Starts the display thread
display_thread.start()
