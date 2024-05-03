from library import server, functions, MediapipeFaceDetection, MouthOpeningRatio, MouthCrop, Tracker, eye_detect
import threading
import queue

image_queue = queue.Queue()
tilt_queue = queue.Queue()
display_image_queue = queue.Queue()
eye_level_queue = queue.Queue()

current_image = None
nose_tracker = None
chin_tracker = None

if __name__ == '__main__':
    functions.check_for_logs_folder()  # Check if the logs folder exists, if not create it
    functions.delete_empty_folders_in_logs()  # Delete empty folders in the logs folder to prevent clutter

    # Initialize face and landmark data
    face_mesh_model = MediapipeFaceDetection.initialize_mediapipe_face_mesh()

    # Starts the server in a new thread
    server_thread = threading.Thread(target=server.start_server, args=(image_queue, tilt_queue, eye_level_queue))
    server_thread.start()

    # Starts the display_images function in a new thread with the functions_image_queue
    functions.start_display_thread(display_image_queue)

while True:
    # Get the image path from the server_image_queue
    image_path = image_queue.get()

    # Display the image
    display_image_queue.put(image_path)

    # Find the state for the image path
    state = functions.find_state_for_image_path(image_path)

    # Do something based on the state
    if state == 'Mouth Opening':
        # Check for eye level
        eye_level = eye_detect.detect_faces_and_landmarks(image_path, face_mesh_model)
        eye_level_queue.put(eye_level)  # Put the eye level into the queue

        # Detect face and generate landmarks
        frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model,
                                                                                  is_image=True)
        if face_landmarks:
            # Calculate mouth opening ratio
            mor = MouthOpeningRatio.calculate_mouth_opening_ratio(face_landmarks)
            print(f"Mouth opening ratio: {mor}")

    elif state == 'Mallampati':
        # Check for eye level
        eye_level = eye_detect.detect_faces_and_landmarks(image_path, face_mesh_model)
        eye_level_queue.put(eye_level)  # Put the eye level into the queue

        # Crop mouth out from images
        frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model,
                                                                                  is_image=True)
        if face_landmarks:
            cropped_image = MouthCrop.crop_mouth_region(frame, face_landmarks)

            # Classify it using mallampati model here and store the class in a list or something maybe
            # Then after a certain amount of images/time, take the mean class(?)

    elif state == 'Neck Movement':
        # eye_level = eye_detect.detect_faces_and_landmarks(image_path, face_mesh_model)
        # eye_level_queue.put(eye_level)  # Put the eye level into the queue

        # Detect face and calculate angle based on nose, mouth points that we track.
        frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model,
                                                                                  is_image=True)
        nose_tracker, chin_tracker, frame = Tracker.add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker,
                                                                              chin_tracker)
    else:
        print("Invalid state")
