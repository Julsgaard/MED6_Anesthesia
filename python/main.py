from library import server, functions, MediapipeFaceDetection, MouthOpeningRatio, MouthCrop, Tracker, eye_detect, mallampati_image_prep, mallampati_CNN_run_model
import threading
import queue

image_queue = queue.Queue()
tilt_queue = queue.Queue()
display_image_queue = queue.Queue()
eye_level_queue = queue.Queue()

current_image = None
nose_tracker = None
chin_tracker = None

predictions = []

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

    # Find the device and load the model for the AI model
    device = mallampati_CNN_run_model.find_device()
    model = mallampati_CNN_run_model.load_model(device, model_path='library/mallampati_models/CNN Models/model_mallampati_CNN_20240506_102522.pth')

    while True:
        # Get the image path from the server image queue
        image_path = image_queue.get()

        # Display the image
        # display_image_queue.put(image_path)

        # Find the state for the image path
        state = functions.find_state_for_image_path(image_path)

        frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model,
                                                                                  is_image=True)
        # Check for eye level
        eye_level = eye_detect.detect_faces_and_landmarks(image_path, face_mesh_model)
        eye_level_queue.put(eye_level)  # Put the eye level into the queue


        # Check the state and run the appropriate functions
        if state == 'Mouth Opening':

            # Display the image
            display_image_queue.put(frame)

            if face_landmarks:
                # Calculate mouth opening ratio
                lip_distance = MouthOpeningRatio.lip_distance_monitor(face_landmarks)
                if lip_distance:
                    print(f"Lip Distance Increase: {lip_distance:.2f}%.")
                    functions.save_results_to_file(image_path, f"Lip Distance Increase: {lip_distance:.2f}%.")


        elif state == 'Mallampati':
            if face_landmarks:
                cropped_image = MouthCrop.crop_mouth_region(frame, face_landmarks)

                # Prepare the image
                transformed_image = mallampati_image_prep.prepare_mallampati_image_for_loader(cropped_image,
                                                                                              image_pixel_size=64)

                # Add a dimension to the image
                image_with_extra_dim = transformed_image.unsqueeze(0)

                # Display the image of the mouth
                display_image_queue.put(image_with_extra_dim[0].numpy().transpose((1, 2, 0)))

                # Run the model
                predicted = mallampati_CNN_run_model.run_predictions_on_image(model, image_with_extra_dim, device)

                if predicted == 0:
                    print("Mallampati Class 1 or 2")

                    # Save the prediction to a file
                    functions.save_results_to_file(image_path, "Mallampati Class 1 or 2")

                    # Add prediction to list
                    predictions.append(0)

                elif predicted == 1:
                    print("Mallampati Class 3 or 4")

                    # Save the prediction to a file
                    functions.save_results_to_file(image_path, "Mallampati Class 3 or 4")

                    # Add prediction to list
                    predictions.append(1)

                # After 20 predictions, take the mean of the predictions
                if len(predictions) >= 20:
                    mean_prediction = sum(predictions) / len(predictions)

                    if mean_prediction < 0.5:
                        print(f"User is predicted to be Mallampati Class 1 or 2 | Mean: {mean_prediction}")
                    else:
                        print(f"User is predicted to be Mallampati Class 3 or 4 | Mean: {mean_prediction}")

                #TODO: We might need a state for Mallampati done, so we can save the final prediction to a file.

        elif state == 'Neck Movement':

            nose_tracker, chin_tracker, frame, head_angle = Tracker.add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker,
                                                                                  chin_tracker)
            if head_angle:
                print(f"Head Angle in degrees: {head_angle}")
                functions.save_results_to_file(image_path, f"Head Angle: {head_angle}")
            # Display the image
            display_image_queue.put(frame)

        elif state == 'Error State':

            display_image_queue.put(frame)

            # Reset default lip distance value
            #MouthOpeningRatio.default_lip_distance = None
            #MouthOpeningRatio.distances = None

            # Reset mallampati predictions
            #predictions = []

            # Reset default tracker value
            #Tracker.default_chin_nose_distance = None

