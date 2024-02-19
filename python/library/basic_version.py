import cv2

# Load the cascade
mouth_cascade = cv2.CascadeClassifier('Cascade/haarcascade_mcs_mouth.xml')

# Load the image
img = cv2.imread('Images/image1.jpg')

# Check if the image was loaded properly
if img is None:
    print("Error: Image not loaded. Check your file path.")
else:
    # Resize the image to a width of 800 pixels
    scale_percent = 800 / img.shape[1]  # Calculate the scaling factor
    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    # Convert to grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Detect the mouth
    mouths = mouth_cascade.detectMultiScale(gray, 1.1, 20)

    # Draw the rectangle around each mouth
    for (x, y, w, h) in mouths:
        cv2.rectangle(resized, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Display
    cv2.imshow('Mouth Detected', resized)
    cv2.waitKey(0)  # Wait indefinitely for a key press

    # Destroy all windows after key press
    cv2.destroyAllWindows()
