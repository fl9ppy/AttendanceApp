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
        style = ThemedStyle(self.root)
        style.set_theme("clam")

        container = ttk.Frame(self.root, padding="20")
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        label = ttk.Label(container, text="Face Recognition", font=("Helvetica", 16))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        name_label = ttk.Label(container, text="Enter your name:", font=("Helvetica", 12))
        name_label.grid(row=1, column=0, pady=5, sticky="E")
        name_entry = ttk.Entry(container, textvariable=self.name, font=("Helvetica", 12))
        name_entry.grid(row=1, column=1, pady=5, sticky="W")

        start_button = ttk.Button(container, text="Start Recognition", command=self.start_recognition, style="Accent.TButton")
        start_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

    def start_recognition(self):
        name = self.name.get()

        if not name:
            messagebox.showwarning("Empty Name", "Please enter your name.")
            return

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()

            face_locations = face_recognition.face_locations(frame)

            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                face_roi = frame[top:bottom, left:right]

                cv2.imshow('Face Detection', frame)

                key = cv2.waitKey(1)
                if key == ord('s'):
                    photo_path = os.path.join(self.save_folder, name + ".jpg")
                    cv2.imwrite(photo_path, face_roi)
                    messagebox.showinfo("Reference Photo Saved", f"Reference photo saved: {photo_path}")
                    cv2.destroyAllWindows()
                    cap.release()
                    return

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()
