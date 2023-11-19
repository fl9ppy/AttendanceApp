import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import os
import numpy as np
import face_recognition
import cv2
import threading
import attendance_uploader
import requests

class FaceRecognizer:
    def __init__(self, known_faces_folder='StudentPhotos'):
        # Initialize the FaceRecognizer with a folder containing known faces
        self.known_faces_folder = known_faces_folder
        self.known_face_encodings, self.known_face_names = self.load_known_faces()

        # Initialize a set to keep track of recognized names
        self.recognized_names = set()

        # Initialize a set to keep track of students marked absent during the current session
        self.absent_marked = set()

        # Initialize a set to keep track of faces seen during recognition
        self.faces_seen = set()

    def load_known_faces(self):
        # Load known faces from images in the specified folder
        known_face_encodings = []
        known_face_names = []

        for filename in os.listdir(self.known_faces_folder):
            if filename.endswith(".jpg"):
                image_path = os.path.join(self.known_faces_folder, filename)
                name = os.path.splitext(filename)[0]

                # Load the image
                face_image = face_recognition.load_image_file(image_path)

                try:
                    # Use the default face detector to get face encodings
                    face_encoding = face_recognition.face_encodings(face_image)[0]

                    known_face_encodings.append(face_encoding)
                    known_face_names.append(name)
                except IndexError:
                    # Print a message if no face is found in the image
                    print(f"No face found in {filename}")

        return known_face_encodings, known_face_names

    def recognize_faces_in_camera(self, attendance_app):
        # Initialize the webcam
        cap = cv2.VideoCapture(0)

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Find face locations in the current frame
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            # If a face is found and not recognized yet, recognize and mark attendance
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Compare face with known faces
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_distance_index = np.argmin(distances)
                min_distance = distances[min_distance_index]

                # Set a threshold for face recognition
                if min_distance < 0.6:
                    name = self.known_face_names[min_distance_index]

                    # Check if the face has already been recognized in this session
                    if name not in self.recognized_names:
                        attendance_app.mark_present_by_name(name)
                        self.recognized_names.add(name)  # Mark the face name as recognized
                        self.faces_seen.add(name)  # Mark the face as seen during recognition

                        # Remove from the absent_marked set if present
                        if name in self.absent_marked:
                            self.absent_marked.remove(name)

                else:
                    name = "Unknown"

                # Draw a rectangle around the face on the frame
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Display the name
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            # Display the resulting frame
            cv2.imshow('Face Recognition', frame)

            # Break the loop when 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the webcam and close all windows
        cap.release()
        cv2.destroyAllWindows()


class AttendanceApp:
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        self.root.title("Attendance Tracker")

        # Initialize attendance dictionary to store attendance data
        self.attendance_dict = {}

        # Initialize the directory where attendance files will be saved
        self.attendance_directory = ""

        # Initialize FaceRecognizer
        self.face_recognizer = FaceRecognizer()

        # Initialize the set to keep track of students marked absent during the current session
        self.absent_marked = set()

        # GUI components
        self.label = tk.Label(root, text="Select Student:")
        self.student_var = tk.StringVar()
        self.student_dropdown = tk.OptionMenu(root, self.student_var, "")
        self.mark_present_btn = tk.Button(root, text="Mark Present", command=self.mark_present)
        self.mark_absent_btn = tk.Button(root, text="Mark Absent", command=self.mark_absent)
        self.finish_class_btn = tk.Button(root, text="Finish Class", command=self.finish_class)
        self.choose_file_btn = tk.Button(root, text="Choose Class File", command=self.choose_class_file)
        self.start_recognition_btn = tk.Button(root, text="Start Face Recognition", command=self.start_face_recognition)

        # Grid layout for GUI components
        self.label.grid(row=0, column=0, padx=10, pady=10)
        self.student_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.mark_present_btn.grid(row=1, column=0, padx=10, pady=10)
        self.mark_absent_btn.grid(row=1, column=1, padx=10, pady=10)
        self.finish_class_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.choose_file_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.start_recognition_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Load class from file when the application starts
        self.class_names = []
        self.load_class_names()

    def load_class_names(self):
        # Open file dialog to select class file and directory
        file_path = filedialog.askopenfilename(title="Select Class File", filetypes=[("Text files", "*.txt")])
        self.attendance_directory = filedialog.askdirectory(title="Choose Attendance Directory")

        if file_path and self.attendance_directory:
            try:
                # Read class names from the selected file, excluding the first line
                with open(file_path, "r") as file:
                    # Skip the first line (header) and strip any leading/trailing whitespaces
                    self.class_names = [line.strip() for line in file.readlines()[1:]]

                # Initialize attendance dictionary for each student
                self.attendance_dict = {name: {"Present": [], "Absent": []} for name in self.class_names}

                # Clear and update the OptionMenu with the loaded class names
                menu = self.student_dropdown['menu']
                menu.delete(0, 'end')
                for name in self.class_names:
                    menu.add_command(label=name, command=lambda value=name: self.student_var.set(value))
                self.student_var.set(self.class_names[0] if self.class_names else "")
            except FileNotFoundError:
                # Display error if the file is not found
                messagebox.showerror("Error", "Class names file not found.")
                self.root.destroy()

    def mark_present(self):
        # Check if a class file is chosen
        if not self.class_names or not self.attendance_directory:
            messagebox.showwarning("Warning", "Please choose a class file and attendance directory first.")
            return
        student_name = self.student_var.get()
        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Update attendance dictionary with present status for the selected student
        self.attendance_dict[student_name]["Present"].append(date)
        messagebox.showinfo("Marked Present", f"{student_name} marked present on {date}")

    def mark_absent(self):
        # Check if a class file is chosen
        if not self.class_names or not self.attendance_directory:
            messagebox.showwarning("Warning", "Please choose a class file and attendance directory first.")
            return
        student_name = self.student_var.get()
        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Update attendance dictionary with absent status for the selected student
        self.attendance_dict[student_name]["Absent"].append(date)
        messagebox.showinfo("Marked Absent", f"{student_name} marked absent on {date}")

        # Add the student to the absent_marked set to prevent duplicate marking during recognition
        self.absent_marked.add(student_name)

    def mark_present_by_name(self, student_name):
        # Check if a class file is chosen
        if not self.class_names or not self.attendance_directory:
            messagebox.showwarning("Warning", "Please choose a class file and attendance directory first.")
            return
        date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update attendance dictionary with present status for the selected student
        if student_name != 'Unknown':
            if student_name not in self.attendance_dict:
                self.attendance_dict[student_name] = {"Present": [], "Absent": []}

            self.attendance_dict[student_name]["Present"].append(date)
            messagebox.showinfo("Marked Present", f"{student_name} marked present on {date}")
        else:
            messagebox.showinfo("Unknown", "Unknown face detected, not marking attendance.")

    def mark_absent_by_name(self, student_name):
        # Check if the student has already been marked absent
        if student_name not in self.absent_marked:
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            # Update attendance dictionary with absent status for the selected student
            if student_name != 'Unknown':
                if student_name not in self.attendance_dict:
                    self.attendance_dict[student_name] = {"Present": [], "Absent": []}

                self.attendance_dict[student_name]["Absent"].append(date)
                messagebox.showinfo("Marked Absent", f"{student_name} marked absent on {date}")

                # Mark the face name as absent and prevent duplicate marking
                self.absent_marked.add(student_name)
            else:
                messagebox.showinfo("Unknown", "Unknown face detected, not marking attendance.")

            
    def save_attendance(self):
        # Check if a class file and attendance directory are chosen
        if not self.class_names or not self.attendance_directory:
            messagebox.showwarning("Warning", "Please choose a class file and attendance directory first.")
            return

        attendance_data = {
            "class_names": self.class_names,
            "attendance_dict": self.attendance_dict
        }

        try:
            print("Making request with method:", requests.post)
            response = requests.post("http://localhost:8000/upload_attendance", json=attendance_data, headers={'Content-Type': 'application/json'})

            
            # Check if the response content type is JSON
            if response.headers['Content-Type'] == 'application/json':
                response_data = response.json()

                # Now you can access the JSON data in response_data
                if response.status_code == 200:
                    messagebox.showinfo("Attendance Uploaded", response_data.get("message", "Attendance data successfully uploaded."))
                else:
                    messagebox.showerror("Error", response_data.get("error", "Failed to upload attendance data."))
            else:
                # Handle the case where the response is not JSON
                messagebox.showerror("Error", "Invalid response format. Expected JSON.")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", "Failed to upload attendance data.")

    def finish_class(self):
        # Check if a class file is chosen
        if not self.class_names or not self.attendance_directory:
            messagebox.showwarning("Warning", "Please choose a class file and attendance directory first.")
            return

        # Iterate over each student and mark as absent if not already marked
        for student_name in self.class_names:
            if student_name not in self.attendance_dict:
                self.attendance_dict[student_name] = {"Present": [], "Absent": []}

            # Mark as absent if not already marked present
            if not self.attendance_dict[student_name]["Present"]:
                date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                self.attendance_dict[student_name]["Absent"].append(date)

        # Save attendance after marking absent for missing students
        self.save_attendance()

    def choose_class_file(self):
        # Open file dialog to choose a class file and directory
        self.load_class_names()

    def start_face_recognition(self):
        # Start face recognition using the FaceRecognizer in a separate thread
        face_recognition_thread = threading.Thread(target=self.face_recognizer.recognize_faces_in_camera, args=(self,))
        face_recognition_thread.start()

if __name__ == "__main__":
    # Create and run the Tkinter application
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()