from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, this is the home page."

@app.route('/upload_attendance/Attendance_Calinescu_Adrian', methods=['GET'])
def upload_attendance():
    print(request)
    if request.is_json:
        data = request.json
    
        class_names = data.get("class_names", [])
        attendance_dict = data.get("attendance_dict", {})
    
        for student_name, attendance_data in attendance_dict.items():
            attendance_file_name = os.path.join("uploads", f"Attendance_{student_name}.txt")
    
            with open(attendance_file_name, "a") as file:
                for new_date in attendance_data["Present"]:
                    file.write(f"- Present:\n    - {new_date}\n")
    
                for new_date in attendance_data["Absent"]:
                    file.write(f"- Absent:\n    - {new_date}\n")

        return jsonify({"message": "Attendance data received successfully."})
    else:
        return jsonify({"error": "Invalid Content-Type. Expected 'application/json'."}), 415  # Unsupported Media Type

if __name__ == '__main__':
    app.run(port=5001, debug=True)
