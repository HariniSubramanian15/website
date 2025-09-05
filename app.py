# Import the necessary libraries from Flask and Python's standard library
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all routes. This is crucial for the frontend to communicate with the backend.
CORS(app)

# Define the file paths for our "database" files
DATA_FOLDER = 'data'
TUTORS_FILE = os.path.join(DATA_FOLDER, 'tutors.json')
STUDENTS_FILE = os.path.join(DATA_FOLDER, 'students.json')

# --- Helper Functions for Data Persistence ---

def ensure_data_files_exist():
    """
    Checks if the data directory and files exist. If not, it creates them
    and initializes them with an empty JSON object.
    This prevents errors when the server starts for the first time.
    """
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(TUTORS_FILE) or os.stat(TUTORS_FILE).st_size == 0:
        with open(TUTORS_FILE, 'w') as f:
            json.dump({}, f)  # Initialize with an empty JSON object
    if not os.path.exists(STUDENTS_FILE) or os.stat(STUDENTS_FILE).st_size == 0:
        with open(STUDENTS_FILE, 'w') as f:
            json.dump({}, f)  # Initialize with an empty JSON object

def load_data(file_path):
    """
    Loads data from a given JSON file.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def save_data(file_path, data):
    """
    Saves data to a given JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4) # Use indent for human-readable format

# --- API Routes for Student and Tutor Management ---

@app.route('/api/register/tutor', methods=['POST'])
def register_tutor():
    """
    API endpoint for a tutor to register their profile.
    It expects a JSON payload with tutor details.
    """
    tutor_data = request.json
    tutor_id = tutor_data.get('id')
    
    if not tutor_id:
        return jsonify({"message": "Tutor ID is required"}), 400

    try:
        data = load_data(TUTORS_FILE)
        
        # Add a new field for notifications, initialized as an empty list
        tutor_data['notifications'] = []
        
        data[tutor_id] = tutor_data
        save_data(TUTORS_FILE, data)
        
        return jsonify({"message": "Tutor profile saved successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to save tutor profile", "error": str(e)}), 500

@app.route('/api/register/student', methods=['POST'])
def register_student():
    """
    API endpoint for a student to register their profile.
    It expects a JSON payload with student details.
    """
    student_data = request.json
    student_id = student_data.get('id')

    if not student_id:
        return jsonify({"message": "Student ID is required"}), 400
    
    try:
        data = load_data(STUDENTS_FILE)
        data[student_id] = student_data
        save_data(STUDENTS_FILE, data)

        return jsonify({"message": "Student profile saved successfully!"}), 201
    except Exception as e:
        return jsonify({"message": "Failed to save student profile", "error": str(e)}), 500

@app.route('/api/tutors', methods=['GET'])
def get_all_tutors():
    """
    API endpoint to get a list of all registered tutors.
    This is what the student's search page will call.
    It excludes sensitive information like notifications from the list.
    """
    try:
        data = load_data(TUTORS_FILE)
        tutor_list = list(data.values())
        
        # Filter out the notifications field to avoid sending it to the client
        filtered_tutors = [{k: v for k, v in tutor.items() if k != 'notifications'} for tutor in tutor_list]
        
        return jsonify(filtered_tutors), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve tutor data", "error": str(e)}), 500

@app.route('/api/tutor/select', methods=['POST'])
def select_tutor():
    """
    API endpoint for a student to select a tutor.
    This adds a notification to the selected tutor's profile.
    """
    request_data = request.json
    tutor_id = request_data.get('tutorId')
    student_id = request_data.get('studentId')
    
    if not tutor_id or not student_id:
        return jsonify({"message": "Tutor ID and Student ID are required"}), 400
        
    try:
        tutor_data = load_data(TUTORS_FILE)
        student_data = load_data(STUDENTS_FILE)
        
        # Check if both the tutor and student exist in our "database"
        if tutor_id not in tutor_data or student_id not in student_data:
            return jsonify({"message": "Tutor or student not found"}), 404
        
        # Create a notification object
        notification = {
            "student_id": student_id,
            "message": f"Student {student_id} is interested in your services.",
            "timestamp": datetime.now().isoformat()
        }
        
        # Append the notification to the tutor's profile
        tutor_data[tutor_id]['notifications'].append(notification)
        save_data(TUTORS_FILE, tutor_data)
        
        return jsonify({"message": "Tutor notified successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to notify tutor", "error": str(e)}), 500

@app.route('/api/tutor/notifications/<string:tutor_id>', methods=['GET'])
def get_tutor_notifications(tutor_id):
    """
    API endpoint for a tutor to check their notifications.
    """
    try:
        tutor_data = load_data(TUTORS_FILE)
        tutor_profile = tutor_data.get(tutor_id)
        
        if not tutor_profile:
            return jsonify({"message": "Tutor not found"}), 404
        
        notifications = tutor_profile.get('notifications', [])
        
        return jsonify({"notifications": notifications}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve notifications", "error": str(e)}), 500

# --- Server Startup ---

if __name__ == '__main__':
    # Ensure the data files are ready before starting the server
    ensure_data_files_exist()
    # Run the server. Setting host to '0.0.0.0' makes it accessible on the local network.
    app.run(host='0.0.0.0', port=5000, debug=True)