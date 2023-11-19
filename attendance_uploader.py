from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def display_json_files():
    json_files = get_json_files()
    json_data = read_json_files(json_files)
    print(json_data)
    return render_template('json_template.html', json_data=json_data)

def get_json_files():
    json_folder = 'uploads'
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    return json_files

def read_json_files(json_files):
    json_all = {}
    json_folder = 'uploads'
    for file_name in json_files:
        file_path = os.path.join(json_folder, file_name)
        with open(file_path, 'r') as file:
            data = file.read()
            json_all[file_name] = data
    return json_all

@app.route('/upload_attendance', methods=['POST', 'GET'])
def upload_attendance():
    print(request.method)  # Print the HTTP method
    print(request.headers)  # Print request headers
    print(request.get_json())  # Print JSON data
    print(request.headers)
    if request.is_json:
        data = request.get_json()
    
        attendance_dict = data.get("attendance_dict", {})
    
        for student_name, attendance_data in attendance_dict.items():
            attendance_file_name = os.path.join("uploads", f"Attendance_{student_name}.json")
            
            json_result = {"results": []}  # Initialize inside the loop for each student

            for new_date in attendance_data["Present"]:
                json_result["results"].append({"type": "present", "date": new_date})

            for new_date in attendance_data["Absent"]:
                json_result["results"].append({"type": "absent", "date": new_date})
        
            with open(attendance_file_name, "w") as file:
                json.dump(json_result, file)  # Directly write JSON data to the file

        return jsonify({"message": "Attendance data received successfully."})
    else:
        return jsonify({"error": "Invalid Content-Type. Expected 'application/json'."}), 415  # Unsupported Media Type

if __name__ == '__main__':
    app.run(port=8000, debug=True)
