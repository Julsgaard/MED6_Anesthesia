import cv2
import numpy as np

def preprocess_image(frame):
    # Convert to a different color space if more suitable for lip detection, e.g., YCrCb or HSV
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

    # Use the Cr channel for lip detection due to its effectiveness in distinguishing lips
    _, cr, _ = cv2.split(ycrcb)
    return cr

def segment_lips(cr_channel):
    # Apply a binary threshold or adaptive threshold to segment the lips
    # Parameters for thresholding may need adjustment for different lighting conditions
    _, thresh = cv2.threshold(cr_channel, 150, 255, cv2.THRESH_BINARY)

    # Apply morphological operations to clean up the segmentation
    kernel = np.ones((3, 3), np.uint8)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return morphed

def find_lip_contours(morphed_image):
    # Find contours from the segmented image
    contours, _ = cv2.findContours(morphed_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # You might want to filter contours here based on size/shape criteria
    lip_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]  # Assume largest contour is lips
    return lip_contours

def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Preprocess the frame to extract the Cr channel
        cr_channel = preprocess_image(frame)

        # Segment the lips from the Cr channel
        segmented_lips = segment_lips(cr_channel)

        # Find contours from the segmented lips
        lip_contours = find_lip_contours(segmented_lips)

        # Draw the contours on the original frame
        cv2.drawContours(frame, lip_contours, -1, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Lip Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
