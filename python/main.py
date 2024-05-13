from library import server, functions, MediapipeFaceDetection, MouthOpeningRatio, MouthCrop, Tracker, eye_detect, \
    mallampati_image_prep, mallampati_CNN_run_model, mallampati_ResNet_run_model, TimerScript
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

# Additional variables to manage state
current_state = None
timer = TimerScript.TimerClass()  # Create an instance of Timer

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

    # Find the device (GPU or CPU)
    device = mallampati_CNN_run_model.find_device()

    # Load the model (either CNN or ResNet)
    # model = mallampati_CNN_run_model.load_model_CNN(device, model_path='library/mallampati_models/model_mallampati_CNN_Best_Model_CUDA.pth')
    model = mallampati_ResNet_run_model.load_model_ResNet(device,
                                                          model_path='library/mallampati_models/loss_0.0183_1000_epochs/model.pth')

    while True:
        # Get the image path from the server image queue
        image_path = image_queue.get()

        # Display the image
        # display_image_queue.put(image_path)

        # Find the state for the image path
        new_state = functions.find_state_for_image_path(image_path)

        #CHECK TO RESET THE TIMER IF THE STATE CHANGES
        if current_state != new_state:
            current_state = new_state
            timer.reset()  # Reset timer when state changes

        frame, face_landmarks = MediapipeFaceDetection.detect_faces_and_landmarks(image_path, face_mesh_model,
                                                                                  is_image=True)
        # Check for eye level
        eye_level = eye_detect.detect_faces_and_landmarks(image_path, face_mesh_model)
        eye_level_queue.put(eye_level)  # Put the eye level into the queue

        # Check the state and run the appropriate functions
        if current_state == 'Mouth Opening':
            # Timer
            time_elapsed = timer.elapsed_time()
            print(f"Time elapsed: {time_elapsed}")
            #Mouth opening state er lidt ligegyldigt om de åbner munden 'for sent', det vigtigste er at de har munden lukket når exercise starter og det må vi gå ud fra de har
            if time_elapsed > 2:  #Give them X amount of time to open their mouth

                # Display the image
                display_image_queue.put(frame)

                if face_landmarks:
                    # Calculate mouth opening ratio
                    lip_distance = MouthOpeningRatio.lip_distance_monitor(face_landmarks)
                    if lip_distance:
                        functions.save_results_to_file_and_print(f"Lip Distance Increase: {lip_distance:.2f}%.", image_path)
            else:
                display_image_queue.put(frame)

        elif current_state == 'Mallampati':
            # Timer
            time_elapsed = timer.elapsed_time()
            print(f"Time elapsed: {time_elapsed}")
            if time_elapsed > 12:  #Give them X amount of time to open their mouth(?)
                # Ved mallampati går der cirka 10 sekunder fra at exercise starter til at avatar siger "now, open your mouth" så ja
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
                        # Save the prediction to a file
                        functions.save_results_to_file_and_print("Mallampati Class 1 or 2", image_path)

                        # Add prediction to list
                        predictions.append(0)

                    elif predicted == 1:
                        # Save the prediction to a file
                        functions.save_results_to_file_and_print("Mallampati Class 3 or 4", image_path)

                        # Add prediction to list
                        predictions.append(1)

                    # After 10 predictions, take the mean of the predictions
                    if len(predictions) >= 10:
                        mean_prediction = sum(predictions) / len(predictions)

                        if mean_prediction < 0.5:
                            functions.save_results_to_file_and_print(
                                f"User is predicted to be Mallampati Class 1 or 2 | Mean: {mean_prediction}",
                                image_path, save_only_results=True)
                        else:
                            functions.save_results_to_file_and_print(
                                f"User is predicted to be Mallampati Class 3 or 4 | Mean: {mean_prediction}",
                                image_path, save_only_results=True)
            else:
                display_image_queue.put(frame)

        elif current_state == 'Neck Movement':
            # Timer
            time_elapsed = timer.elapsed_time()
            print(f"Time elapsed: {time_elapsed}")
            if time_elapsed > 2:  #Give them X amount of time to open their mouth(?)
                # Head tilt er det også bare vigtigt at de har head i neutral position i starten. Ellers er det vigtigste at vi ved hvornår det er forward tilt og back tilt
                nose_tracker, chin_tracker, frame, head_angle = Tracker.add_chin_and_nose_tracker(frame, face_landmarks,
                                                                                                  nose_tracker,
                                                                                                  chin_tracker)
                if head_angle:
                    # print(f"Head Angle in degrees: {head_angle}")

                    if time_elapsed < 35:  #Der går cirka 35 sekunder fra at exercise starter til at avatar siger "now, tilt your head forward"
                        functions.save_results_to_file_and_print(f"Upper head angle: {head_angle}", image_path)

                    else:
                        lower_head_angle = head_angle
                        functions.save_results_to_file_and_print(f"Lower head angle: {head_angle}", image_path)

                display_image_queue.put(frame)

            else:
                display_image_queue.put(frame)

        elif current_state == 'Error State':

            display_image_queue.put(frame)
            display_image_queue.empty()  # This might not be necessary, but it's here just in case

            # Reset default lip distance value
            #MouthOpeningRatio.default_lip_distance = None
            #MouthOpeningRatio.distances = None

            # Reset mallampati predictions
            #predictions = []

            # Reset default tracker value
            #Tracker.default_chin_nose_distance = None
