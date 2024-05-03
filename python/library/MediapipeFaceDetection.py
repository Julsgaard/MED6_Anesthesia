import cv2
import mediapipe as mp
from library import MouthOpeningRatio, Tracker
#import Tracker #Udkommenter den her linje hvis du vil teste scriptet direkte


inner_lip_indices = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
#lip_and_mouth_indices = [33,263,61,291]
chin_tracker = None
nose_tracker = None

def detect_faces_and_landmarks(source, face_mesh, is_image=False):
    """Returns the facial landmarks and the frame with the landmarks drawn on it, needs either a video capture or an
    image, as well as the MediaPipe Face Mesh object. Set is_image to true if the source is an image instead of a
    video capture"""

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

    # Convert the BGR image to RGB.
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and find faces and their landmarks.
    results = face_mesh.process(image_rgb)

    # Check if any faces were found
    if not results.multi_face_landmarks:
        # No faces found, return the original frame and None for the landmarks
        print("No faces detected.")
        return frame, None
    for face_landmarks in results.multi_face_landmarks:
        for idx, landmark in enumerate(face_landmarks.landmark):
            if idx in inner_lip_indices:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                #cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # Draw circle for each specified landmark
                # Draw the index number near each landmark point
                #cv2.putText(frame, str(idx), (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    return frame, results.multi_face_landmarks[0].landmark

def initialize_mediapipe_face_mesh():
    """Initializes the MediaPipe Face Mesh and returns it."""
    # Initialize MediaPipe Face Mesh.
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.3,
        refine_landmarks=True)

    return face_mesh


if __name__ == "__main__":
    # Initialize mediapipe
    face_mesh = initialize_mediapipe_face_mesh()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        # Exit loop on 'q' keypress
        frame, face_landmarks = detect_faces_and_landmarks(cap, face_mesh)

        #area = MouthOpeningArea.calculate_mouth_opening_area(face_landmarks)
        #print(f"Area: {area}")

        nose_tracker, chin_tracker, frame = Tracker.add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker,chin_tracker)




        # Display the resulting frame
        cv2.imshow('Facial Landmarks', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()

