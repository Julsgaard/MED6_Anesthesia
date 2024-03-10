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

        # Default to 0.0 if 'tiltAngle' is not provided
        tilt_angle = request.form.get('tiltAngle', '0.0')


        # Here, convert tilt_angle from string to float, and handle potential conversion errors
        try:
            tilt_angle = float(tilt_angle)
        except ValueError:
            # If there is an error, set a default value or handle it as needed
            tilt_angle = 0.0

        print(f"Tilt angle: {tilt_angle}")

        if image_path:
            # Now you can use the tilt_angle along with the image
            # For example, put both in the queue if needed
            image_queue.put(image_path)

            return jsonify(message="Image received and updated successfully!")
        else:
            return jsonify(message="Image path is None"), 400
    else:
        return jsonify(message="No image received"), 400




