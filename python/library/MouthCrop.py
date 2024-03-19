import cv2

def crop_mouth_region(frame, landmarks):
    """
    Crops the mouth region from the image based on specified landmarks and ensures
    that the resulting cropped image is a square with equal x and y dimensions.

    Parameters:
        frame: The image from which the mouth region will be cropped.
        landmarks: A list containing the landmarks of the face. Each landmark
                   should be a class with 'x' and 'y' attributes (like the ones returned
                   by MediaPipe) representing the landmark's relative position in the image.

    Returns:
        The cropped image containing the mouth region, adjusted to be a square.
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
