import cv2
import dlib

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


            # Draw facial landmarks
            for i, n in enumerate(range(48, 68)):  # Mouth landmarks in Dlib's 68 point model
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # Use a different color for mouth landmarks if you like
                #cv2.putText(frame, str(n), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

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
