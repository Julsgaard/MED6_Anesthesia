from library import server, functions, MediapipeFaceDetection, OldHeadAngle, MouthOpeningArea, MouthCrop, Tracker, EyeDetect
import threading
import queue

image_queue = queue.Queue()
tilt_queue = queue.Queue()
display_image_queue = queue.Queue()

current_image = None
nose_tracker = None
chin_tracker = None

global eye_within_threshold #BRAIN

if __name__ == '__main__':
    functions.check_for_logs_folder()  # Check if the logs folder exists, if not create it
    functions.delete_empty_folders_in_logs()  # Delete empty folders in the logs folder to prevent clutter

    eye_within_threshold = 1 #BRAIN
    # Initialize face and landmark data
    face_mesh_model = MediapipeFaceDetection.initialize_mediapipe_face_mesh()

    #Initialize eye data
    eye_mesh_model = EyeDetect.initialize_mediapipe_eye_placement()

    # Starts the server in a new thread
    server_thread = threading.Thread(target=server.start_server, args=(image_queue, tilt_queue))
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
        # print("State is Mouth Opening")
        eye_within_threshold = EyeDetect.detect_faces_and_landmarks(image_path, eye_mesh_model, is_image=True)


    elif state == 'Mallampati':
        # print("State is Mallampati")
        frame, face_landmarks = EyeDetect.detect_faces_and_landmarks(image_path, eye_mesh_model, is_image=True)

    elif state == 'Neck Movement':
        # print("State is Neck Movement")
        frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model, is_image=True)
        nose_tracker, chin_tracker, frame, chin_nose_distance = Tracker.add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker,
                                                                                  chin_tracker)
        if chin_nose_distance is not None:
             print(f"Distance between chin and nose is: {chin_nose_distance}")


    else:
        print("Invalid state")

    # print(f"Received image: {image_path}")
    # Neck angle using only the phone sensor (Needs 20 entries to calculate, which is like 8-10 seconds? (Maybe i should make it time based instead))
    # absolute_neck_angle, default_tilt_angle = NeckAngle_PhoneSensor.store_and_calculate_absolute_tilt_angle(tilt_queue.get())

    # Detect faces and landmarks
    # frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model,
    #                                                                           is_image=True)
    #
    # if face_landmarks:
    #     nose_tracker, chin_tracker, frame = Tracker.add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker,
    #                                                                           chin_tracker)
    #     # HeadAngle.store_head_angle_information(tilt_queue.get(), face_landmarks,image_path)
    #     display_image_queue.put(frame)
    # else:
    #     display_image_queue.put(frame)
