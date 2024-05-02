import cv2
import mediapipe as mp

left_eye_indices = [252, 253, 254, 255, 256, 263, 339, 341, 359, 362, 384, 385, 386, 387, 388, 398, 463, 466, 477]
right_eye_indices = [22, 23, 24, 25, 26, 33, 110, 130, 133, 153, 154, 155, 157, 158, 159, 160, 161, 173, 246]

# Initialize video capture
cap = cv2.VideoCapture(0)

MIN_Y_THRESHOLD = 0.1  # Minimum y-coordinate (as a fraction of the frame height)
MAX_Y_THRESHOLD = 0.9  # Maximum y-coordinate (as a fraction of the frame height)
UPPER_Y_THRESHOLD = 0.45  # Upper y-coordinate threshold (as a fraction of the frame height)
LOWER_Y_THRESHOLD = 0.55  # Lower y-coordinate threshold (as a fraction of the frame height)
left_eye_avg_y = None  # Initialize outside the loop
right_eye_avg_y = None

eye_within_threshold = 0


# Initialize Mediapipe solutions

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
        # for face_landmarks in results.multi_face_landmarks:
        #     for idx, landmark in enumerate(face_landmarks.landmark):
        #         if idx in left_eye_indices:
        #             x = int(landmark.x * frame.shape[1])
        #             y = int(landmark.y * frame.shape[0])
        #             cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # Draw circle for each specified landmark
        #             # Calculate average position for left eye
        #             left_eye_avg_y = sum([y for i in range(1, len(left_eye_indices), 2)]) / (len(left_eye_indices) // 2)
        #     for idx, landmark in enumerate(face_landmarks.landmark):
        #         if idx in right_eye_indices:
        #             x = int(landmark.x * frame.shape[1])
        #             y = int(landmark.y * frame.shape[0])
        #             #cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # Draw circle for each specified landmark
        #             # Calculate average position for right eye
        #             #right_eye_avg_y = sum([y for i in range(1, len(right_eye_indices), 2)]) / ( len(right_eye_indices) // 2)

        eye_landmarks_combined = (right_eye_avg_y + left_eye_avg_y) / 2
        eye_avg_y = sum([eye_landmarks_combined]) / len([eye_landmarks_combined])

        # rect_top_left = (int(frame.shape[1] * 0.35), int(frame.shape[0] / 9))
        # rect_bottom_right = (int(frame.shape[1] * 0.65), int(frame.shape[0] * 0.25))
        # text_y = int(frame.shape[0] / 5)
        # overlay = frame.copy()
        # alpha = 0.4  # Opacity of the rectangle
        if MIN_Y_THRESHOLD * frame.shape[0] < eye_avg_y < MAX_Y_THRESHOLD * frame.shape[0]:
            if eye_avg_y < UPPER_Y_THRESHOLD * frame.shape[0]:
                eye_within_threshold = 0
                # cv2.rectangle(overlay, rect_top_left, rect_bottom_right, (0, 0, 0), cv2.FILLED)
                # cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                # cv2.rectangle(frame, rect_top_left, rect_bottom_right, (220, 220, 220), 2, cv2.LINE_AA)
                # text_width = cv2.getTextSize("Eyes Too High", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0][0]
                # text_x = int((frame.shape[1] - text_width) / 2)
                # cv2.putText(frame, "Eyes Too High", (text_x, text_y),
                # cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            elif eye_avg_y > LOWER_Y_THRESHOLD * frame.shape[0]:
                eye_within_threshold = 2
                # cv2.rectangle(overlay, rect_top_left, rect_bottom_right, (0, 0, 0), cv2.FILLED)
                # cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                # cv2.rectangle(frame, rect_top_left, rect_bottom_right, (220, 220, 220), 2, cv2.LINE_AA)
                # text_width = cv2.getTextSize("Eyes Too Low", cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0][0]
                # text_x = int((frame.shape[1] - text_width) / 2)
                # cv2.putText(frame, "Eyes Too Low", (text_x, text_y),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                eye_within_threshold = 1
                print("Eyes Position:", eye_avg_y)

    return eye_within_threshold


def initialize_mediapipe_eye_placement():
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
    face_mesh = initialize_mediapipe_eye_placement()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        # Exit loop on 'q' keypress
        eye_within_threshold = detect_faces_and_landmarks(cap, face_mesh)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()
