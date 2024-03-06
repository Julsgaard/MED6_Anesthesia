from scipy.spatial import distance as dist



#Takes the list of facial landmarks and calculates the mouth opening area
def calculate_mouth_opening_area(points): #MOR/MAR is from https://www.researchgate.net/profile/Zaheed-Shaikh/publication/325228756_Driver_Fatigue_Detection_and_Alert_System_using_Non-Intrusive_Eye_and_Yawn_Detection/links/631f9b890a70852150eb4ae7/Driver-Fatigue-Detection-and-Alert-System-using-Non-Intrusive-Eye-and-Yawn-Detection.pdf
    lip_points = [(points.part(n).x, points.part(n).y) for n in range(60, 68)] #Extracts the lip points
    A = dist.euclidean(lip_points[1], lip_points[5])
    B = dist.euclidean(lip_points[2], lip_points[4])
    C = dist.euclidean(lip_points[0], lip_points[3])
    mor = (A + B) / (2.0 * C)

    return mor


def calculate_polygon_area(points): #USES SHOELACE FORMULA https://en.wikipedia.org/wiki/Shoelace_formula
    lip_points = [(points.part(n).x, points.part(n).y) for n in range(60, 68)] #Extracts the lip points
    n = len(lip_points)  # Number of points
    area = 0.0
    for i in range(n):
        j = (i + 1) % n  # Next vertex index
        area += lip_points[i][0] * lip_points[j][1]
        area -= lip_points[j][0] * lip_points[i][1]
    area = abs(area) / 2.0
    return area
