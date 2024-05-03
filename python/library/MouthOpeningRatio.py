from scipy.spatial import distance as dist


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
