import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from library import functions

app = Flask(__name__)

image_queue = None


def start_server(host_ip, server_port, queue):
    global image_queue
    image_queue = queue
    app.run(debug=False, host=host_ip, port=server_port, threaded=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'picture' in request.files:
        file = request.files['picture']
        filename = file.filename
        filename = secure_filename(filename)

        image_path = os.path.join(functions.session_path, filename)
        file.save(image_path)

        if image_path is None:
            return jsonify(message="Image path is None"), 400

        # Put the image path into the queue
        image_queue.put(image_path)

        return jsonify(message="Image received and updated successfully!")
    else:
        return jsonify(message="No image received"), 400




