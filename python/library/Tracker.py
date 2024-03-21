import cv2

def initialize_tracker(frame, initial_position):
    """Initializes the tracker for the specified region."""
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, initial_position)
    return tracker

def update_tracker(frame, tracker):
    """Updates the tracker with the new frame."""
    success, new_position = tracker.update(frame)
    if success:
        return new_position
    return None

def draw_tracking_box(frame, bbox):
    """Draws the tracking box on the frame."""
    if bbox:  # Ensure the bounding box is valid
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
    return frame

def normalize_to_pixels(normalized_x, normalized_y, frame_width, frame_height, box_size):
    """Converts normalized coordinates into pixel coordinates."""
    x = int(normalized_x * frame_width - box_size / 2)
    y = int(normalized_y * frame_height - box_size / 2)
    return x, y

def add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker, chin_tracker):
    """Creates or updates chin and nose trackers."""
    box_size = 20  # Define the size of the tracking box
    frame_height, frame_width = frame.shape[:2]

    if nose_tracker is None or chin_tracker is None:
        nose_x, nose_y = normalize_to_pixels(face_landmarks[4].x, face_landmarks[4].y, frame_width, frame_height, box_size)
        chin_x, chin_y = normalize_to_pixels(face_landmarks[152].x, face_landmarks[152].y, frame_width, frame_height, box_size)

        print(f"Initial Nose Tracker Position: {nose_x}, {nose_y}, {box_size}, {box_size}")
        print(f"Initial Chin Tracker Position: {chin_x}, {chin_y}, {box_size}, {box_size}")

        if nose_tracker is None:
            nose_tracker = initialize_tracker(frame, (nose_x, nose_y, box_size, box_size))
        if chin_tracker is None:
            chin_tracker = initialize_tracker(frame, (chin_x, chin_y, box_size, box_size))

        frame = draw_tracking_box(frame, (nose_x, nose_y, box_size, box_size))
        frame = draw_tracking_box(frame, (chin_x, chin_y, box_size, box_size))
    else:
        new_nose_position = update_tracker(frame, nose_tracker)
        print(f"Updated Nose Position: {new_nose_position}")
        if new_nose_position:
            frame = draw_tracking_box(frame, new_nose_position)
        else:
            print("Nose tracking failed")

        new_chin_position = update_tracker(frame, chin_tracker)
        print(f"Updated Chin Position: {new_chin_position}")
        if new_chin_position:
            frame = draw_tracking_box(frame, new_chin_position)
        else:
            print("Chin tracking failed")

    return nose_tracker, chin_tracker, frame
