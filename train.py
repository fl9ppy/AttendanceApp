import cv2
import face_recognition
import os

# Variables
save_folder = "StudentPhotos"
name = input("Enter your name: ")

# Create the folder if it doesn't exist
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Initialize the OpenCV camera
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Find all face locations in the frame
    face_locations = face_recognition.face_locations(frame)

    # Draw rectangles around the faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Crop the face region
        face_roi = frame[top:bottom, left:right]

        # Save the cropped face as a reference photo
        key = cv2.waitKey(1)
        if key == ord('s'):
            photo_path = os.path.join(save_folder, name + ".jpg")
            cv2.imwrite(photo_path, face_roi)
            print(f"Reference photo saved: {photo_path}")
            break

    # Display the resulting frame
    cv2.imshow('Face Detection', frame)

# Release the capture
cap.release()
cv2.destroyAllWindows()
