import cv2
import dlib

from library.MouthOpeningArea import calculate_mouth_opening_area
from library.HeadAngle import calculate_default_face_angle


# Method that returns the facial landmarks and the frame with the landmarks drawn on it, needs the video capture, the face cascade and the ladnmark predictor
def detect_faces_and_landmarks(source, face_cascade, predictor, is_image=False):
    # Read a frame from video capture or use the provided image
    if is_image:
        frame = source
    else:
        ret, frame = source.read()
        if not ret:
            print("Failed to grab frame")
            return None, None

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using Haar Cascade
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None, frame  # Return None for landmarks and the original frame if no faces are detected

    # Convert faces to Dlib rectangles to use with the predictor
    for (x, y, w, h) in faces:
        dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
        landmarks = predictor(gray, dlib_rect)

        for n in range(0, 68):  # Draw the 68 facial landmarks
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)
            cv2.putText(frame, str(n), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        return landmarks, frame

def initialize_face_and_landmark_data():
    face_cascade = cv2.CascadeClassifier('HaarCascadeData/haarcascade_frontalface_default.xml')
    predictor_path = "FacialLandmarkData/shape_predictor_68_face_landmarks.dat"
    predictor = dlib.shape_predictor(predictor_path)
    return face_cascade, predictor

if __name__ == "__main__":
    # Initialize video capture with DirectShow API
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_cascade, predictor = initialize_face_and_landmark_data()

    while True:
        # Read frame and detect landmarks
        face_landmarks, frame = detect_faces_and_landmarks(cap, face_cascade, predictor)

        # Process the detected landmarks
        if face_landmarks is not None:
            lip_area = calculate_mouth_opening_area(face_landmarks)
            print(lip_area)

            default_face_angle = calculate_default_face_angle(face_landmarks)
            print(f"Default face ratio is {default_face_angle}")
        else:
            print("No facial landmarks detected.")

        # Display the resulting frame
        cv2.imshow('Facial Landmarks', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()



#Method to initialize the face cascade and the landmark predictor (This is now a seperate method from the landmark detection because we only want to do it once)
def initialize_face_and_landmark_data():
    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier('HaarCascadeData/haarcascade_frontalface_default.xml')
    # Initialize Dlib's facial landmark predictor
    predictor_path = "FacialLandmarkData/shape_predictor_68_face_landmarks.dat"  # Path to the trained model
    predictor = dlib.shape_predictor(predictor_path)
    return face_cascade, predictor


if __name__ == "__main__":
    # Initialize video capture with DirectShow API
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_cascade, predictor = initialize_face_and_landmark_data()

    while True:
        # Exit loop on 'q' keypress
        face_landmarks, frame = detect_faces_and_landmarks(cap, face_cascade, predictor)

        if face_landmarks is not None:  # Check if landmarks were detected
            lip_area = calculate_mouth_opening_area(face_landmarks)
            print(lip_area)

            default_face_angle = calculate_default_face_angle(face_landmarks)
            print(f"Default face ratio is {default_face_angle}")
        else:  # Handle the case when no landmarks are detected
            print("No facial landmarks detected.")

        # Display the resulting frame
        cv2.imshow('Facial Landmarks', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
