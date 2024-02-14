import cv2
import mediapipe as mp

# Initialize MediaPipe Face Mesh.
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize drawing utils for drawing landmarks on the face.
mp_drawing = mp.solutions.drawing_utils

# Inner lip landmarks indices based on MediaPipe Face Mesh
inner_lip_indices = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

# Start capturing video from the webcam.
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Convert the BGR image to RGB.
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find faces and their landmarks.
    results = face_mesh.process(image_rgb)

    # Draw face landmarks.
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx in inner_lip_indices:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * image.shape[1])
                y = int(landmark.y * image.shape[0])
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)  # Draw circle for each inner lip landmark

    # Show the frame with the inner lip landmarks.
    cv2.imshow('Inner Lip Detection in Live Video', image)
    if cv2.waitKey(5) & 0xFF == 27:  # Press 'ESC' to exit.
        break

# Release the webcam and close OpenCV windows.
cap.release()
cv2.destroyAllWindows()

# Release MediaPipe resources.
face_mesh.close()
