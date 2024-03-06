from scipy.spatial import distance as dist

#This script is used to calculate the head angle of the user, approach is taken from: https://onlinelibrary.wiley.com/doi/full/10.1002/tee.22778?casa_token=T35tTv7eXwEAAAAA%3AVhGzW-bADbqZ22Y9fNclHeLL1Xm44YLfpjImIzjVJexRZ0oJCSEuyi7IIZwETKTpPMVsPbo9fk2H0w

def calculate_face_ratio(points):
    """Calculates the face ratio of the user, using the distance between the eyes and the mouth
    :param points: The facial landmarks
    :return: The face ratio"""

    eye_and_mouth_points = [(points.part(n).x, points.part(n).y) for n in [17, 26, 60, 64]]

    eye_distance = dist.euclidean(eye_and_mouth_points[0], eye_and_mouth_points[1])
    mouth_distance = dist.euclidean(eye_and_mouth_points[2], eye_and_mouth_points[3])
    face_ratio = eye_distance/mouth_distance

    return face_ratio


def calculate_face_angle(DFR,CFR):
    """Calculates the face angle of the user, based on the default face angle and the current face angle

    :param DFR: The default face ratio
    :param CFR: The current face ratio
    :return: The face angle"""
    face_angle = (CFR-DFR)/0.05
    return face_angle


def calculate_neck_angle(phone_angles, face_angles):
    """Calculate the average of the sum of phone angles and face angles.

    :param phone_angles: A list of angles for the phone for each observation.
    :param face_angles: A list of angles for the face for each observation.
    :return: The neck angle -> The average of the sum of phone angles and face angles."""
    if len(phone_angles) != len(face_angles):
        raise ValueError("phone_angles and face_angles must have the same length.")

    n = len(phone_angles)  # Number of observations
    total_sum = 0

    for i in range(n):
        total_sum += (phone_angles[i] + face_angles[i])

    neck_angle = total_sum / n
    return neck_angle


if __name__ == "__main__":
    print("Not meant to be run directly")