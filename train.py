import cv2
import face_recognition
import os

# Variables
save_folder = "ReferencePhotos"
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

    # Display the resulting frame
    cv2.imshow('Face Detection', frame)

    # Check if the user pressed the 's' key to save a photo
    if cv2.waitKey(1) & 0xFF == ord('s') and len(face_locations) > 0:
        # Save the photo in the specified folder
        photo_path = os.path.join(save_folder, name + ".jpg")
        cv2.imwrite(photo_path, frame)
        print(f"Reference photo saved: {photo_path}")
        break

# Release the capture
cap.release()
cv2.destroyAllWindows()
