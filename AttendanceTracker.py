import tkinter as tk
from tkinter import ttk

class AttendanceApp:
    def __init__(self, root, student_names):
        self.root = root
        self.root.title("Attendance Marking App")

        self.student_names = student_names
        self.attendance_status = {name: tk.StringVar() for name in student_names}

        self.create_widgets()

    def create_widgets(self):
        # Create a label
        label = tk.Label(self.root, text="Mark Attendance")
        label.pack(pady=10)

        # Create a treeview to display student names and attendance status
        self.tree = ttk.Treeview(self.root, columns=('Name', 'Status'))
        self.tree.heading('#0', text='Name')
        self.tree.heading('#1', text='Status')
        self.tree.column('#1', stretch=tk.YES)
        self.tree.pack(pady=10)

        # Add student names to the treeview
        for name in self.student_names:
            self.tree.insert('', 'end', text=name, values=(name, 'Present'), tags=('present',))

        # Create buttons to mark attendance
        present_button = tk.Button(self.root, text="Mark Present", command=self.mark_present)
        present_button.pack(side=tk.LEFT, padx=10)

        absent_button = tk.Button(self.root, text="Mark Absent", command=self.mark_absent)
        absent_button.pack(side=tk.RIGHT, padx=10)

    def mark_present(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_name = self.tree.item(selected_item, 'text')
            self.attendance_status[selected_name].set('Present')
            self.tree.item(selected_item, values=(selected_name, 'Present'), tags=('present',))
        else:
            tk.messagebox.showwarning("No Selection", "Please select a student to mark as present.")

    def mark_absent(self):
        selected_item = self.tree.selection()
        if selected_item:
            selected_name = self.tree.item(selected_item, 'text')
            self.attendance_status[selected_name].set('Absent')
            self.tree.item(selected_item, values=(selected_name, 'Absent'), tags=('absent',))
        else:
            tk.messagebox.showwarning("No Selection", "Please select a student to mark as absent.")


if __name__ == "__main__":
    # Replace the list below with the actual student names
    student_names = ["Student 1", "Student 2", "Student 3", "Student 4"]

    root = tk.Tk()
    app = AttendanceApp(root, student_names)
    root.mainloop()
