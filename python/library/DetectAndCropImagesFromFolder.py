import cv2
import mediapipe as mp
import os  # Import the os module to interact with the file system

# Define landmarks for inner lips and mouth region
inner_lip_indices = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

def crop_mouth_region(frame, landmarks):
    """
    Crops the mouth region from the image and ensures the cropped region is square.
    """
    # Ensure landmarks are provided for indices 0, 18, 57, and 287
    if len(landmarks) < 288:
        print("Insufficient landmarks provided.")
        return None

    # Extract coordinates for specific landmarks around the mouth
    points = [landmarks[164], landmarks[175], landmarks[57], landmarks[287]]
    x_coords = [int(point.x * frame.shape[1]) for point in points]
    y_coords = [int(point.y * frame.shape[0]) for point in points]

    # Find the bounding box for the mouth region
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    # Calculate the size of the bounding box
    width = x_max - x_min
    height = y_max - y_min

    # Determine the size of the square
    side_length = max(width, height)

    # Center the square around the original center of the mouth region
    center_x = (x_min + x_max) // 2
    center_y = (y_min + y_max) // 2

    # Calculate new min and max x and y coordinates to ensure the crop is a square
    x_min = max(0, center_x - side_length // 2)
    x_max = min(frame.shape[1], center_x + side_length // 2)
    y_min = max(0, center_y - side_length // 2)
    y_max = min(frame.shape[0], center_y + side_length // 2)

    # Ensure the square doesn't exceed the original image boundaries
    if x_max - x_min < side_length:
        # Adjust x_min if possible
        if x_min > 0:
            x_min = max(0, x_max - side_length)
        # Otherwise, adjust x_max
        elif x_max < frame.shape[1]:
            x_max = min(frame.shape[1], x_min + side_length)

    if y_max - y_min < side_length:
        # Adjust y_min if possible
        if y_min > 0:
            y_min = max(0, y_max - side_length)
        # Otherwise, adjust y_max
        elif y_max < frame.shape[0]:
            y_max = min(frame.shape[0], y_min + side_length)

    # Crop the image to the new square region
    cropped_image = frame[y_min:y_max, x_min:x_max]

    return cropped_image


def detect_faces_and_landmarks(image_path, face_mesh):
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Failed to load image from {image_path}")
        return None, False

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)
    if not results.multi_face_landmarks:
        print("No faces detected.")
        return frame, False  # Return frame and False indicating no faces detected

    # Assuming you process the first face found
    face_landmarks = results.multi_face_landmarks[0]
    cropped_mouth = crop_mouth_region(frame, face_landmarks.landmark)
    return cropped_mouth, True  # Return cropped mouth and True indicating face(s) detected

def initialize_mediapipe_face_mesh():
    """
    Initializes the MediaPipe Face Mesh.
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5, refine_landmarks=True)
    return face_mesh

if __name__ == "__main__":
    face_mesh = initialize_mediapipe_face_mesh()
    image_folder_path = 'UncroppedImages'
    save_folder_path = 'CroppedImages'
    no_faces_folder_path = 'NoFaceImages'  # Folder for images where no faces are detected

    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)
    if not os.path.exists(no_faces_folder_path):
        os.makedirs(no_faces_folder_path)

    for filename in os.listdir(image_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder_path, filename)
            cropped_frame, faces_detected = detect_faces_and_landmarks(image_path, face_mesh)
            if faces_detected:
                save_path = os.path.join(save_folder_path, 'cropped_' + filename)
                cv2.imwrite(save_path, cropped_frame)
                print(f"Cropped image saved to {save_path}")
            else:
                no_face_save_path = os.path.join(no_faces_folder_path, filename)
                cv2.imwrite(no_face_save_path, cropped_frame)
                print(f"Image with no faces saved to {no_face_save_path}")

    cv2.destroyAllWindows()
    face_mesh.close()
