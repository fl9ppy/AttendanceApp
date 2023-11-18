import face_recognition
import cv2

# Load the reference photo (the known face)
reference_image_path = "path/to/reference/photo.jpg"
reference_image = face_recognition.load_image_file(reference_image_path)
reference_encoding = face_recognition.face_encodings(reference_image)[0]

# Initialize the OpenCV camera
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Find all face locations in the frame
    face_locations = face_recognition.face_locations(frame)
    
    # Find face encodings for all faces in the frame
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        # Compare the current face encoding with the reference encoding
        results = face_recognition.compare_faces([reference_encoding], face_encoding)

        if results[0]:
            print("Face recognized!")
        else:
            print("Face not recognized.")

    # Draw rectangles around the faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Face Recognition', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
