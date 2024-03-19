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
    """
    Detects faces and landmarks in an image.
    """
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Failed to load image from {image_path}")
        return None, None

    # Convert the BGR image to RGB.
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and find faces and their landmarks.
    results = face_mesh.process(image_rgb)

    # Check if any faces were found
    if not results.multi_face_landmarks:
        print("No faces detected.")
        return frame, None

    # Draw face landmarks for specific indices and crop the mouth region
    for face_landmarks in results.multi_face_landmarks:
        for idx, landmark in enumerate(face_landmarks.landmark):
            if idx in inner_lip_indices:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
        # Crop the mouth region from the frame
        cropped_mouth = crop_mouth_region(frame, face_landmarks.landmark)
        return cropped_mouth, face_landmarks.landmark  # Return the cropped mouth region

    return frame, None

def initialize_mediapipe_face_mesh():
    """
    Initializes the MediaPipe Face Mesh.
    """
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5, refine_landmarks=True)
    return face_mesh

if __name__ == "__main__":
    face_mesh = initialize_mediapipe_face_mesh()
    image_folder_path = 'MallampatiTrainingData'  # Path to your folder containing images
    save_folder_path = 'Cropped_images'  # Path to the folder where cropped images will be saved

    # Create the save folder if it doesn't exist
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)

    for filename in os.listdir(image_folder_path):
        image_path = os.path.join(image_folder_path, filename)
        # Check if the file is an image
        if image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            cropped_frame, _ = detect_faces_and_landmarks(image_path, face_mesh)
            if cropped_frame is not None:
                # Construct the path for saving the cropped image
                save_path = os.path.join(save_folder_path, 'cropped_' + filename)
                # Save the cropped image
                cv2.imwrite(save_path, cropped_frame)
                print(f"Cropped image saved to {save_path}")

    # Cleanup
    cv2.destroyAllWindows()
    face_mesh.close()
