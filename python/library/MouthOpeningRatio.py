from scipy.spatial import distance as dist
import numpy as np
import statistics

default_inner_lip_distance = None
num_data_points = 5  # Antallet af distancer den bruger ti at beregne default lip distance. Tager median værdien af disse.
distances = []



def calculate_mouth_opening_ratio(face_landmarks):
    """Calculates the mouth opening ratio (MOR) based on specified MediaPipe facial landmarks."""
    # Updated indices for MediaPipe
    indices = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

    # Extracts the lip points from the updated indices, assuming face_landmarks is a flat list of landmarks
    lip_points = [(face_landmarks[i].x, face_landmarks[i].y) for i in indices]

    # We need to define which points A, B, and C refer to in your new landmark scheme
    # Update these based on the actual points used for mouth opening calculation
    A = dist.euclidean(lip_points[3], lip_points[17])  # Update indices based on your measurement points
    B = dist.euclidean(lip_points[7], lip_points[14])  # Same here
    C = dist.euclidean(lip_points[0], lip_points[10])  # And here

    mor = (A + B) / (2.0 * C)
    return mor


def calculate_polygon_area(face_landmarks):
    """Calculates the area of the mouth polygon based on specified MediaPipe facial landmarks using the Shoelace formula."""
    # Updated indices for MediaPipe
    indices = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

    # Extracts the lip points from the updated indices
    lip_points = [(face_landmarks[i].x, face_landmarks[i].y) for i in indices]

    n = len(lip_points)  # Number of points
    area = 0.0
    for i in range(n):
        j = (i + 1) % n  # Next vertex index
        area += lip_points[i][0] * lip_points[j][1]
        area -= lip_points[j][0] * lip_points[i][1]
    area = abs(area) / 2.0

    return area


def calculate_distance(landmark1, landmark2):
    """Calculate the Euclidean distance between two landmarks."""
    return ((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2) ** 0.5


def lip_distance_monitor(landmarks):
    global default_inner_lip_distance
    # Calculate current distance between landmarks 12 and 14
    current_distance = calculate_distance(landmarks[12], landmarks[14])
    distances.append(current_distance)

    if len(distances) < num_data_points:
        print(f"Collecting initial data points ({len(distances)}/{num_data_points}).")
    else:
        if default_inner_lip_distance is None:
            # Calculate the median of the collected distances
            default_inner_lip_distance = statistics.median(distances)
            #print(f"Default inner lip distance set using median: {default_inner_lip_distance:.2f}")
        else:
            # Calculate the difference in percentage
            difference = ((current_distance - default_inner_lip_distance) / default_inner_lip_distance) * 100
            #print(f"The difference from the default inner lip distance is {difference:.2f}%.")
            return difference
