from scipy.spatial import distance as dist

#This script is used to calculate the head angle of the user, approach is taken from: https://onlinelibrary.wiley.com/doi/full/10.1002/tee.22778?casa_token=T35tTv7eXwEAAAAA%3AVhGzW-bADbqZ22Y9fNclHeLL1Xm44YLfpjImIzjVJexRZ0oJCSEuyi7IIZwETKTpPMVsPbo9fk2H0w

phone_angle_list = [] #A list to store the phone angles for each picture
face_ratio_list = [] # A list to store the face ratio for each picture
face_angle_list = [] # A list to store the face angle for each picture

def calculate_face_ratio(points):
    """Calculates the face ratio of the user, using the distance between the eyes and the mouth
    :param points: The facial landmarks
    :return: The face ratio"""

    eye_and_mouth_points = [(points.part(n).x, points.part(n).y) for n in [36, 45 , 60, 64]] #

    eye_distance = dist.euclidean(eye_and_mouth_points[0], eye_and_mouth_points[1])
    mouth_distance = dist.euclidean(eye_and_mouth_points[2], eye_and_mouth_points[3])
    face_ratio = eye_distance/mouth_distance

    return face_ratio


def calculate_face_angle(face_ratio_list):
    """Calculates the face angle of the user, based on the default face angle and the current face angle

    :param face_ratio_list: A list of face ratios for each observation, should be at least 15 observations
    :return: The face angle"""

    #Calculate the DFR based on the mean of the first 5 entries in the face ratio list
    DFR = sum(face_ratio_list[:5])/5
    #Calculate the CFR based on the mean of the last 5 entries in the face ratio list
    CFR = sum(face_ratio_list[-5:])/5


    face_angle = (CFR-DFR)/0.05
    print(f"Face angle: {face_angle}")
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


def store_head_angle_information(phone_angle, face_landmarks):
    print(f"Face ratio is: {calculate_face_ratio(face_landmarks)}")
    #phone_angle_list.append(phone_angle)
    #face_ratio_list.append(calculate_face_ratio(face_landmarks))
    #print(f"Face ratio list: {face_ratio_list}")
    #print(f"Phone angle list: {phone_angle_list}")

    #if len(face_ratio_list) >= 10: #If we data from at least 15 pictures (or any number that we settle on), we can calculate the face angle
    #    calculate_face_angle(face_ratio_list)
    #    phone_angle_list.clear() #Clears both lists after the face angle has been calculated
    #    face_ratio_list.clear()



if __name__ == "__main__":
    print("Not meant to be run directly")