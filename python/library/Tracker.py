import cv2
import math

default_chin_nose_distance = None  # Initialize the default distance to None


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
    if bbox:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
    return frame

def calculate_distance(center1, center2):
    """Calculates the Euclidean distance between the centers of two bounding boxes."""
    return math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

def calculate_angle(default_distance, current_distance):
    """Calculate the angle based on the change in distance."""
    #TODO vinkel er ikke robust i forhold til distance mellem user og camera. Hvis useren bevæger sig hoved for meget væk/på kameraet
    # efter at default_distance er blevet calculated, vil vinklen ikke passe. Måske benyt en slags ratio til at beregne vinkel i stedet?

    # Calculate the ratio of the adjacent side to the hypotenuse
    cosine_value = current_distance / default_distance
    #print(f"Initial cosine_value: {cosine_value}")

    # Egentligt har jeg byttet rundt på current_distance og default_distance i forhold til hvilken der svarer til adjacent og
    # hypotenusen, fordi ellers ender vi med en hypotenuse der er mindre end adjacent, men i mit hoved svarer det til den samme vinkel,
    # bare flipped(??)


    # Clamp the cosine_value to the valid range of -1 to 1 to avoid math domain errors
    cosine_value = max(-1, min(1, cosine_value))
    #print(f"Clamped cosine_value: {cosine_value}")

    # Calculate the angle in radians using the arccosine function
    angle_in_radians = math.acos(cosine_value)
    #print(f"Angle in radians: {angle_in_radians}")

    # Convert radians to degrees
    angle_degrees = math.degrees(angle_in_radians)
    print(f"Angle in degrees: {angle_degrees}")

    return angle_degrees


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
    x = max(0, min(x, frame_width - w))
    y = max(0, min(y, frame_height - h))
    return (x, y, w, h)


def add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker, chin_tracker):
    global default_chin_nose_distance
    box_size = 20  # Box size for tracking
    frame_height, frame_width = frame.shape[:2]

    # Initialize positions for error handling
    initial_nose_position = (0, 0, box_size, box_size)
    initial_chin_position = (0, 0, box_size, box_size)

    if face_landmarks is not None and len(face_landmarks) > 152:
        nose_x, nose_y = int(face_landmarks[9].x * frame_width - box_size / 2), int(
            face_landmarks[9].y * frame_height - box_size / 2)
        chin_x, chin_y = int(face_landmarks[17].x * frame_width - box_size / 2), int(
            face_landmarks[17].y * frame_height - box_size / 2)

        initial_nose_position = ensure_bbox_within_frame((nose_x, nose_y, box_size, box_size), frame_width,
                                                         frame_height)
        initial_chin_position = ensure_bbox_within_frame((chin_x, chin_y, box_size, box_size), frame_width,
                                                         frame_height)

        nose_tracker = initialize_tracker(frame, initial_nose_position)
        chin_tracker = initialize_tracker(frame, initial_chin_position)
    else:
        # Update trackers with last known positions or attempt to reinitialize
        nose_tracker, temp_nose_position = manage_tracking(frame, nose_tracker, initial_nose_position)
        initial_nose_position = temp_nose_position if temp_nose_position is not None else initial_nose_position

        chin_tracker, temp_chin_position = manage_tracking(frame, chin_tracker, initial_chin_position)
        initial_chin_position = temp_chin_position if temp_chin_position is not None else initial_chin_position

    frame = draw_tracking_box(frame, initial_nose_position)
    frame = draw_tracking_box(frame, initial_chin_position)
    nose_center = (initial_nose_position[0] + box_size // 2, initial_nose_position[1] + box_size // 2)
    chin_center = (initial_chin_position[0] + box_size // 2, initial_chin_position[1] + box_size // 2)
    current_chin_nose_distance = calculate_distance(nose_center, chin_center)

    if default_chin_nose_distance is None:
        default_chin_nose_distance = current_chin_nose_distance
        angle = 0
    else:
        angle = calculate_angle(default_chin_nose_distance, current_chin_nose_distance)

    return nose_tracker, chin_tracker, frame, angle

# Example usage:
# frame = cv2.imread('path_to_image.jpg')
# face_landmarks = detect_face_landmarks(frame)  # Assuming a function to detect landmarks
# nose_tracker, chin_tracker = None, None
# nose_tracker, chin_tracker, updated_frame = add_chin_and_nose_tracker(frame, face_landmarks, nose_tracker, chin_tracker)
