import cv2
import face_recognition
import os
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition App")

        self.save_folder = "StudentPhotos"
        self.name = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Create a themed style
        style = ThemedStyle(self.root)
        style.set_theme("equilux")

        # Create a label
        label = ttk.Label(self.root, text="Face Recognition")
        label.grid(row=0, column=0, columnspan=2, pady=10)

        # Entry for entering name
        name_label = ttk.Label(self.root, text="Enter your name:")
        name_label.grid(row=1, column=0, pady=5, sticky="E")
        name_entry = ttk.Entry(self.root, textvariable=self.name)
        name_entry.grid(row=1, column=1, pady=5, sticky="W")

        # Button to start face recognition
        start_button = ttk.Button(self.root, text="Start Recognition", command=self.start_recognition)
        start_button.grid(row=2, column=0, columnspan=2, pady=10)

    def start_recognition(self):
        # Get the name entered by the user
        name = self.name.get()

        # Check if the name is empty
        if not name:
            messagebox.showwarning("Empty Name", "Please enter your name.")
            return

        # Create the folder if it doesn't exist
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

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

                # Display the resulting frame
                cv2.imshow('Face Detection', frame)

                # Save the cropped face as a reference photo when the 's' key is pressed
                key = cv2.waitKey(1)
                if key == ord('s'):
                    photo_path = os.path.join(self.save_folder, name + ".jpg")
                    cv2.imwrite(photo_path, face_roi)
                    messagebox.showinfo("Reference Photo Saved", f"Reference photo saved: {photo_path}")
                    cv2.destroyAllWindows()
                    cap.release()
                    return

            # Check for the 'q' key to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
