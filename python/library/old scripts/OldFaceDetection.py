import cv2
import dlib
import os
from library.MouthOpeningRatio import calculate_mouth_opening_area
from library.HeadAngle_ImageProcessing import calculate_face_ratio


#TODO Måske ændre sådan at funktionerne virker på en række af billeder (måske 10) i stedet for en stream af billeder? Alternativt kunne man måske også bare lave en anden funktion til det HMMM


def detect_faces_and_landmarks(source, cascade, shape_predictor, is_image=False):
    """Returns the facial landmarks and the frame with the landmarks drawn on it, needs the video
    capture, the face cascade and the landmark predictor"""

    # Read a frame from video capture or use the provided image
    if is_image:
        # Load the image from the path if source is a path
        frame = cv2.imread(source)
        if frame is None:
            print(f"Failed to load image from {source}")
            return None, None
    else:
        ret, frame = source.read()
        if not ret:
            print("Failed to grab frame")
            return None, None

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using Haar Cascade
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return None, frame  # Return None for landmarks and the original frame if no faces are detected

    # Convert faces to Dlib rectangles to use with the predictor
    for (x, y, w, h) in faces:
        dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
        landmarks = shape_predictor(gray, dlib_rect)

        for n in range(0, 68):  # Draw the 68 facial landmarks
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)
            cv2.putText(frame, str(n), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        return landmarks, frame


def initialize_face_and_landmark_data():
    """Initializes the face cascade and the landmark predictor and returns them as a tuple."""
    # Constructing an absolute path to the HaarCascade and Dlib model files
    base_dir = os.path.dirname(os.path.realpath(__file__))  # Gets the directory of the current script
    haar_cascade_path = os.path.join(base_dir, 'HaarCascadeData', 'haarcascade_frontalface_default.xml')
    dlib_predictor_path = os.path.join(base_dir, 'FacialLandmarkData', 'shape_predictor_68_face_landmarks.dat')

    face_cas = cv2.CascadeClassifier(haar_cascade_path)
    shape_predictor = dlib.shape_predictor(dlib_predictor_path)
    return face_cas, shape_predictor


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

            face_ratio = calculate_face_ratio(face_landmarks)
            print(f"Face ratio is {face_ratio}")
        else:  # Handle the case when no landmarks are detected
            print("No facial landmarks detected.")

        # Display the resulting frame
        cv2.imshow('Facial Landmarks', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
