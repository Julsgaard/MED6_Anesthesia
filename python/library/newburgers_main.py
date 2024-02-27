import cv2
import dlib
import math
from scipy.spatial import distance as dist

def calculate_mouth_opening_area(points): #MOR/MAR is from https://www.researchgate.net/profile/Zaheed-Shaikh/publication/325228756_Driver_Fatigue_Detection_and_Alert_System_using_Non-Intrusive_Eye_and_Yawn_Detection/links/631f9b890a70852150eb4ae7/Driver-Fatigue-Detection-and-Alert-System-using-Non-Intrusive-Eye-and-Yawn-Detection.pdf
    A = dist.euclidean(points[1], points[5])
    B = dist.euclidean(points[2], points[4])
    C = dist.euclidean(points[0], points[3])
    mor = (A + B) / (2.0 * C)

    print(f"Mouth opening area is {mor}")

    return mor

def calculate_polygon_area(points): #USES SHOELACE FORMULA https://en.wikipedia.org/wiki/Shoelace_formula
    n = len(points)  # Number of points
    area = 0.0
    for i in range(n):
        j = (i + 1) % n  # Next vertex index
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    area = abs(area) / 2.0
    print(f"Inner lip area: {area}")
    return area

def detect_faces_and_landmarks(video_source=0):
    # Initialize video capture with DirectShow API
    cap = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)

    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier('HaarCascadeData/haarcascade_frontalface_default.xml')

    # Initialize Dlib's facial landmark predictor
    predictor_path = "FacialLandmarkData/shape_predictor_68_face_landmarks.dat"  # Path to the trained model
    predictor = dlib.shape_predictor(predictor_path)
    detector = dlib.get_frontal_face_detector()

    while True:
        # Read a frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces using Haar Cascade
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Convert faces to Dlib rectangles to use with the predictor
        for (x, y, w, h) in faces:
            # Convert to a dlib rectangle
            dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))

            # Use Dlib to get facial landmarks
            landmarks = predictor(gray, dlib_rect)

            # Draw facial landmarks and calculate area for inner lip contour
            lip_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(60, 68)]
            #lip_area = calculate_polygon_area(lip_points)


            calculate_mouth_opening_area(lip_points)

            for n in range(0, 68):  # There are 68 landmark points
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)
                if n >= 60 and n <= 67:  # Optionally, draw numbers for the lip landmarks
                    cv2.putText(frame, str(n), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

        # Display the resulting frame
        cv2.imshow('Facial Landmarks', frame)

        # Exit loop on 'q' keypress
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

# Ensure you have the 'shape_predictor_68_face_landmarks.dat' model file in your working directory or specify the correct path.
detect_faces_and_landmarks()


