import numpy as np
from scipy.spatial import distance as dist



#This script is used to calculate the head angle of the user, approach is taken from: https://onlinelibrary.wiley.com/doi/full/10.1002/tee.22778?casa_token=T35tTv7eXwEAAAAA%3AVhGzW-bADbqZ22Y9fNclHeLL1Xm44YLfpjImIzjVJexRZ0oJCSEuyi7IIZwETKTpPMVsPbo9fk2H0w

#This function takes facial landmark points and calculates the defeault face angle (the ratio between eye and mouth distance
def calculate_default_face_angle(points):
    eye_and_mouth_points = [(points.part(n).x, points.part(n).y) for n in [17, 26, 60, 64]]

    eye_distance = dist.euclidean(eye_and_mouth_points[0], eye_and_mouth_points[1])
    mouth_distance = dist.euclidean(eye_and_mouth_points[2], eye_and_mouth_points[3])
    DFR = eye_distance/mouth_distance

    return DFR







if __name__ == "__main__":
    print("Hello World")