import cv2

def find_mouth_opening(image_path):
    # Initialize mouth_opening to None
    mouth_opening = None

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not loaded. Check the file path.")
        return None

    # Resize image for display
    screen_res = 1280, 720
    scale_width = screen_res[0] / image.shape[1]
    scale_height = screen_res[1] / image.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(image.shape[1] * scale)
    window_height = int(image.shape[0] * scale)
    resized_image = cv2.resize(image, (window_width, window_height))

    # Convert to grayscale
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Load Haar Cascade classifiers for face and mouth
    face_cascade = cv2.CascadeClassifier('Cascade/haarcascade_frontalface_default.xml')
    mouth_cascade = cv2.CascadeClassifier('Cascade/haarcascade_mcs_mouth.xml')

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    if len(faces) == 0:
        print("No faces detected.")
        return None

    for (x, y, w, h) in faces:
        # Focus on the lower half of the face for mouth detection
        roi_gray = gray[y + h // 2:y + h, x:x + w]

        # Detect mouth within the face region
        mouths = mouth_cascade.detectMultiScale(roi_gray, 1.5, 5)
        if len(mouths) == 0:
            print("No mouth detected.")
            continue

        for (mx, my, mw, mh) in mouths:
            # Draw rectangle around the mouth
            cv2.rectangle(resized_image, (x + mx, y + h // 2 + my), (x + mx + mw, y + h // 2 + my + mh), (0, 255, 0), 3)

            # Calculate the mouth opening distance
            mouth_opening = mh
            print(f"Mouth Opening: {mouth_opening} pixels")
            break  # Consider only the first detected mouth

        break  # Consider only the first detected face

    # Show the output image
    cv2.imshow("Mouth Detection", resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return mouth_opening

# Test the function with an image
mouth_opening = find_mouth_opening('Images/image1.jpg')
if mouth_opening is not None:
    print(f"Mouth Opening: {mouth_opening} pixels")
else:
    print("Mouth was not detected in the image.")
