import os
import cv2 as cv
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from library import functions
import threading

app = Flask(__name__)

latest_image = None
lock = threading.Lock()

image_queue = None


def start_server(host_ip, server_port, queue):
    global image_queue
    image_queue = queue
    app.run(debug=False, host=host_ip, port=server_port, threaded=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    global latest_image
    if 'picture' in request.files:
        file = request.files['picture']
        filename = file.filename
        filename = secure_filename(filename)

        image_path = os.path.join(functions.session_path, filename)
        file.save(image_path)

        # Put the image path into the queue
        image_queue.put(image_path)

        with lock:
            latest_image = cv.imread(image_path)

        return jsonify(message="Image received and updated successfully!")
    else:
        return jsonify(message="No image received"), 400


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
