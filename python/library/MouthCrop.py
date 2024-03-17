import cv2


def crop_mouth_region(frame, landmarks):
    """
    Crops the mouth region from the image based on specified landmarks.

    Parameters:
        frame: The image from which the mouth region will be cropped.
        landmarks: A list containing the landmarks of the face. Each landmark
                   should be a class with 'x' and 'y' attributes (like the ones returned
                   by MediaPipe) representing the landmark's relative position in the image.

    Returns:
        The cropped image containing the mouth region.
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

    # Crop the image to the mouth region
    cropped_image = frame[y_min:y_max, x_min:x_max]

    return cropped_image
