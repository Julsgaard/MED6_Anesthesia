from library import server, functions, MediapipeFaceDetection, HeadAngle, MouthOpeningArea, MouthCrop
import threading
import queue

host_ip = '0.0.0.0'
server_port = 5000

server_image_queue = queue.Queue()
tilt_queue = queue.Queue()
display_image_queue = queue.Queue()

current_image = None

if __name__ == '__main__':
    functions.check_for_logs_folder()
    functions.delete_empty_folders_in_logs()
    functions.create_session_folder()

    # Initialize face and landmark data
    face_mesh_model = MediapipeFaceDetection.initialize_mediapipe_face_mesh()

    print("Server starting...")

    # Starts the server in a new thread
    server_thread = threading.Thread(target=server.start_server, args=(host_ip, server_port, server_image_queue, tilt_queue))
    server_thread.start()

    # Starts the display_images function in a new thread with the functions_image_queue
    functions.start_display_thread(display_image_queue)

while True:
    # Get the image path from the server_image_queue
    image_path = server_image_queue.get()
    #print(f"Queue tilt angle {tilt_queue.get()}")
    #print(f"Processing image: {image_path}")




    # display_image_queue.put(image_path)

    # Detect faces and landmarks
    frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model, is_image=True)

    if face_landmarks:
        HeadAngle.store_head_angle_information(tilt_queue.get(), face_landmarks,image_path)
        mouth_region = MouthCrop.crop_mouth_region(frame, face_landmarks)
        #print(f"Face landmarks: {face_landmarks}")
        #MOR = MouthOpeningArea.calculate_polygon_area(face_landmarks)
        #print(f"Mouth opening area: {MOR}")


    display_image_queue.put(frame)



    # print(f"Display image queue size: {display_image_queue.qsize()}")
    # print(f"Server image queue size: {server_image_queue.qsize()}")

