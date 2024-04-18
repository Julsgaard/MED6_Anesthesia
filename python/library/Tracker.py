import cv2
import math

def initialize_tracker(frame, initial_position):
    """Initializes the tracker for the specified region."""
    tracker = cv2.TrackerCSRT_create()
    tracker.init(frame, initial_position)
    return tracker

def update_tracker(frame, tracker):
    """Updates the tracker with the new frame and handles failures."""
    try:
        success, new_position = tracker.update(frame)
        if success:
            return new_position
        else:
            print("Tracking update failed - object may be lost")
            return None
    except Exception as e:
        print(f"An error occurred during tracking: {e}")
        return None

def draw_tracking_box(frame, bbox):
    """Draws the tracking box on the frame."""
    if bbox:  # Ensure the bounding box is valid
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
    return frame

def normalize_to_pixels(normalized_x, normalized_y, frame_width, frame_height, box_size):
    """Converts normalized coordinates into pixel coordinates."""
    x = int(normalized_x * frame_width - box_size / 2)
    y = int(normalized_y * frame_height - box_size / 2)
    return x, y

def calculate_distance(center1, center2):
    """Calculates the Euclidean distance between the centers of two bounding boxes."""
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

def manage_tracking(frame, tracker, initial_position):
    """Attempts to update tracker or reinitialize if tracking fails."""
    new_position = update_tracker(frame, tracker)
    if new_position is None:
        print("Attempting to reinitialize tracker...")
        tracker = initialize_tracker(frame, initial_position)
    return tracker, new_position

def ensure_bbox_within_frame(bbox, frame_width, frame_height):
    """Ensure the bounding box stays within the frame dimensions."""
    x, y, w, h = bbox
    x = max(0, min(x, frame_width - w))  # Ensure x is within [0, frame_width - w]
    y = max(0, min(y, frame_height - h))  # Ensure y is within [0, frame_height - h]
    return (x, y, w, h)

def add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker, chin_tracker):
    box_size = 40  # Increased the size of the tracking box to 40
    frame_height, frame_width = frame.shape[:2]
    distance = None  # Initialize distance to None

    if face_landmarks is not None and len(face_landmarks) > 152:
        nose_x, nose_y = normalize_to_pixels(face_landmarks[4].x, face_landmarks[4].y, frame_width, frame_height, box_size)
        chin_x, chin_y = normalize_to_pixels(face_landmarks[152].x, face_landmarks[152].y, frame_width, frame_height, box_size)

        initial_nose_position = (nose_x, nose_y, box_size, box_size)
        initial_chin_position = (chin_x, chin_y, box_size, box_size)

        # Adjust positions to ensure they are within frame bounds
        initial_nose_position = ensure_bbox_within_frame(initial_nose_position, frame_width, frame_height)
        initial_chin_position = ensure_bbox_within_frame(initial_chin_position, frame_width, frame_height)

        #print(f"Reinitializing Nose Tracker Position: {initial_nose_position}")
        #print(f"Reinitializing Chin Tracker Position: {initial_chin_position}")

        nose_tracker = initialize_tracker(frame, initial_nose_position)
        chin_tracker = initialize_tracker(frame, initial_chin_position)
    else:
        # Use last known positions if no new landmarks are detected
        if nose_tracker is not None and chin_tracker is not None:
            nose_tracker, new_nose_position = manage_tracking(frame, nose_tracker, (0, 0, box_size, box_size))  # Default to zero position
            chin_tracker, new_chin_position = manage_tracking(frame, chin_tracker, (0, 0, box_size, box_size))  # Default to zero position

            if new_nose_position:
                initial_nose_position = new_nose_position
            else:
                initial_nose_position = (0, 0, box_size, box_size)  # Default to zero position

            if new_chin_position:
                initial_chin_position = new_chin_position
            else:
                initial_chin_position = (0, 0, box_size, box_size)  # Default to zero position

        initial_nose_position = ensure_bbox_within_frame(initial_nose_position, frame_width, frame_height)
        initial_chin_position = ensure_bbox_within_frame(initial_chin_position, frame_width, frame_height)

    # Draw tracking boxes and calculate distance if trackers exist
    if nose_tracker and chin_tracker:
        frame = draw_tracking_box(frame, initial_nose_position)
        frame = draw_tracking_box(frame, initial_chin_position)
        nose_center = (initial_nose_position[0] + initial_nose_position[2] / 2, initial_nose_position[1] + initial_nose_position[3] / 2)
        chin_center = (initial_chin_position[0] + initial_chin_position[2] / 2, initial_chin_position[1] + initial_chin_position[3] / 2)
        distance = calculate_distance(nose_center, chin_center)
        print(f"Distance between noseand chin centers: {distance}")

    return nose_tracker, chin_tracker, frame, distance



