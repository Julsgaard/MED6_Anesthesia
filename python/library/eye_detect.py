import cv2

# Indices for the landmarks corresponding to left and right eyes
left_eye_indices = [252, 253, 254, 255, 256, 263, 339, 341, 359, 362, 384, 385, 386, 387, 388, 398, 463, 466, 477]
right_eye_indices = [22, 23, 24, 25, 26, 33, 110, 130, 133, 153, 154, 155, 157, 158, 159, 160, 161, 173, 246]

# Thresholds for eye positioning
UPPER_Y_THRESHOLD = 0.35  # Upper y-coordinate threshold (as a fraction of the frame height)
LOWER_Y_THRESHOLD = 0.65  # Lower y-coordinate threshold (as a fraction of the frame height)


def detect_faces_and_landmarks(source, face_mesh, is_image=True):
    """
    Returns the eye threshold level based on the position of the eyes in the frame.
    The level is 0 if the eyes are within the threshold, 1 if the eyes are too high, and 2 if the eyes are too low.
    """

    if is_image:
        frame = cv2.imread(source)
    else:
        ret, frame = source.read()

    if frame is None:
        print("Failed to grab frame")
        return -1

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)

    if not results.multi_face_landmarks:
        #print("No faces detected.")
        return 0

    for face_landmarks in results.multi_face_landmarks:
        left_eye_y = sum(face_landmarks.landmark[i].y for i in left_eye_indices) / len(left_eye_indices)
        right_eye_y = sum(face_landmarks.landmark[i].y for i in right_eye_indices) / len(right_eye_indices)
        eye_avg_y = (left_eye_y + right_eye_y) / 2  # Average position of both eyes

        if eye_avg_y < UPPER_Y_THRESHOLD:
            #print("Eyes too high")
            return 3  # Eyes too high
        elif eye_avg_y > LOWER_Y_THRESHOLD:
            #print("Eyes too low")
            return 2  # Eyes too low
        else:
            #print("Eyes within threshold")
            return 1  # Eyes within threshold

    return -2
