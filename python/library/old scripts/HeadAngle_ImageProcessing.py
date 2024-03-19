from scipy.spatial import distance as dist
import cv2

#This script is used to calculate the head angle of the user, approach is taken from: https://onlinelibrary.wiley.com/doi/full/10.1002/tee.22778?casa_token=T35tTv7eXwEAAAAA%3AVhGzW-bADbqZ22Y9fNclHeLL1Xm44YLfpjImIzjVJexRZ0oJCSEuyi7IIZwETKTpPMVsPbo9fk2H0w

phone_angle_list = [] #A list to store the phone angles for each picture
face_ratio_list = [] # A list to store the face ratio for each picture
face_angle_list = [] # A list to store the face angle for each picture


def calculate_face_ratio(face_landmarks, image_path):
    """Calculates the face ratio based on the distance from the forehead to the chin.

    :param face_landmarks: The facial landmarks from MediaPipe.
    :param image_path: The path to the image file from which landmarks were detected.
    :return: The face ratio based on the vertical distance from the forehead to the chin."""

    # Read the image to get its dimensions
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image at path {image_path} could not be found or opened.")

    frame_height, frame_width = image.shape[:2]

    # Get the coordinates for the forehead and chin landmarks
    forehead = (int(face_landmarks[10].x * frame_width),
                int(face_landmarks[10].y * frame_height))
    chin = (int(face_landmarks[152].x * frame_width),
            int(face_landmarks[152].y * frame_height))

    # Calculate the vertical distance between the forehead and the chin
    vertical_distance = dist.euclidean(forehead, chin)

    print(f"Vertical distance: {vertical_distance}")

    # For the face ratio, in this context, we might just return the vertical distance directly,
    # or normalize it by some other facial dimension if necessary for your analysis.
    # Here, we'll just return the distance directly:
    return vertical_distance



def calculate_face_angle(face_ratio_list):
    """Calculates the face angle based on vertical face ratios.

    :param face_ratio_list: A list of vertical face ratios for each observation, should be at least 15 observations
    :return: The estimated face angle"""

    if len(face_ratio_list) < 5:
        raise ValueError("Not enough observations to calculate face angle.")

    # Calculate the Default Face Ratio (DFR) and Current Face Ratio (CFR)
    DFR = sum(face_ratio_list[:5]) / 5
    CFR = sum(face_ratio_list[-5:]) / 5

    # Calculate face angle based on the change in vertical face ratio
    face_angle = (CFR - DFR) / 1
    return face_angle

def calculate_neck_angle(phone_angles, face_angles):
    """Calculates the neck angle based on phone and face angles.

    :param phone_angles: A list of phone angles for each observation.
    :param face_angles: A list of face angles for each observation.
    :return: The average neck angle calculated from phone and face angles."""
    if len(phone_angles) != len(face_angles):
        raise ValueError("phone_angles and face_angles must have the same length.")

    # Calculate the average of the sum of phone and face angles
    neck_angle = sum(phone_angle + face_angle for phone_angle, face_angle in zip(phone_angles, face_angles)) / len(phone_angles)
    return neck_angle

def store_head_angle_information(phone_angle, face_landmarks, image_path):
    """Stores head angle information based on vertical facial measurements and calculates metrics.

    :param phone_angle: The current phone angle measurement.
    :param face_landmarks: The facial landmarks detected by MediaPipe.
    :param image_path: The path to the image file used for detecting landmarks."""
    face_ratio = calculate_face_ratio(face_landmarks, image_path)
    face_ratio_list.append(face_ratio)
    phone_angle_list.append(phone_angle)

    print(f"Current vertical face length (ratio): {face_ratio}")

    if len(face_ratio_list) >= 15:  # Ensuring enough data points for analysis
        face_angle = calculate_face_angle(face_ratio_list)
        neck_angle = calculate_neck_angle(phone_angle_list, [face_angle] * len(phone_angle_list))  # Assuming face_angle remains constant for simplification
        print(f"Calculated face angle: {face_angle}")
        print(f"Calculated neck angle: {neck_angle}")

        # Optional: Clear lists after calculations if needed
        phone_angle_list.clear()
        face_ratio_list.clear()




if __name__ == "__main__":
    print("Not meant to be run directly")