from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import hashlib
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# ---------- Serve Frontend HTML Files ----------
@app.route('/')
def index():
    return send_from_directory('../frontend', 'login.html')

@app.route('/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('../frontend', filename)

# ---------- Mock Database ----------
users = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest()
}

students = [
    {'reg_no': '23MIS0077', 'name': 'Kowshik M', 'course': 'M.Tech SE', 'cgpa': 8.5, 'attendance': 85,
     'grades': [{'subject': 'Software Engg', 'grade': 'A'}, {'subject': 'Cloud Computing', 'grade': 'B+'}],
     'semester': 1},
    {'reg_no': '23MIS0104', 'name': 'Sudharsan R', 'course': 'M.Tech SE', 'cgpa': 8.7, 'attendance': 90,
     'grades': [{'subject': 'Software Engg', 'grade': 'A+'}, {'subject': 'Cloud Computing', 'grade': 'A'}],
     'semester': 1},
    {'reg_no': '23MIS0102', 'name': 'Prem P', 'course': 'M.Tech SE', 'cgpa': 8.6, 'attendance': 78,
     'grades': [{'subject': 'Software Engg', 'grade': 'A'}, {'subject': 'Cloud Computing', 'grade': 'B+'}],
     'semester': 1},
    {'reg_no': '24MIS1001', 'name': 'Arun Kumar', 'course': 'M.Tech AI', 'cgpa': 8.9, 'attendance': 92,
     'grades': [{'subject': 'Machine Learning', 'grade': 'A'}, {'subject': 'Data Science', 'grade': 'A+'}],
     'semester': 1},
    {'reg_no': '24MIS1002', 'name': 'Divya Lakshmi', 'course': 'M.Tech DS', 'cgpa': 8.8, 'attendance': 88,
     'grades': [{'subject': 'Data Mining', 'grade': 'A'}, {'subject': 'Statistics', 'grade': 'A'}],
     'semester': 1},
    {'reg_no': '24MIS1003', 'name': 'Bharath Raj', 'course': 'M.Tech SE', 'cgpa': 8.4, 'attendance': 76,
     'grades': [{'subject': 'Software Engg', 'grade': 'B+'}, {'subject': 'Cloud Computing', 'grade': 'B'}],
     'semester': 1},
]

courses = [
    {'id': 1, 'name': 'Software Engineering', 'credits': 4, 'enrolled': 3},
    {'id': 2, 'name': 'Cloud Computing', 'credits': 3, 'enrolled': 2},
    {'id': 3, 'name': 'Machine Learning', 'credits': 4, 'enrolled': 1},
    {'id': 4, 'name': 'Data Science', 'credits': 3, 'enrolled': 1},
]

# Grade point mapping
grade_points = {'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C': 6, 'D': 5, 'F': 0}

def compute_gpa(grades):
    if not grades:
        return 0.0
    total_points = 0
    for g in grades:
        gp = grade_points.get(g['grade'], 0)
        # Assume each subject has 3 credits for simplicity
        total_points += gp * 3
    return round(total_points / (len(grades) * 3), 2)

# Helper to recompute CGPA for all students
def update_all_cgpa():
    for s in students:
        s['cgpa'] = compute_gpa(s.get('grades', []))

update_all_cgpa()

# ---------- Helper Functions ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_reg_number(reg_no):
    return bool(re.match(r'^\d{2}[A-Z]{3}\d{4}$', reg_no))

# ---------- API Endpoints ----------
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'app': 'Student Management System'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in users and users[username] == hash_password(password):
        session['user'] = username
        return jsonify({'success': True, 'message': 'Login successful'})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/students', methods=['GET'])
def get_students():
    search = request.args.get('search', '').lower()
    course_filter = request.args.get('course', '')
    filtered = students
    if search:
        filtered = [s for s in filtered if search in s['name'].lower() or search in s['reg_no'].lower()]
    if course_filter:
        filtered = [s for s in filtered if s['course'] == course_filter]
    return jsonify(filtered)

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    reg_no = data.get('reg_no')
    name = data.get('name')
    course = data.get('course')
    attendance = data.get('attendance', 80)
    grades = data.get('grades', [])
    if not validate_reg_number(reg_no):
        return jsonify({'error': 'Invalid registration number format'}), 400
    cgpa = compute_gpa(grades)
    students.append({'reg_no': reg_no, 'name': name, 'course': course, 'cgpa': cgpa, 'attendance': attendance, 'grades': grades, 'semester': 1})
    return jsonify({'success': True, 'message': 'Student added'})

@app.route('/api/students/<reg_no>', methods=['PUT'])
def update_student(reg_no):
    data = request.json
    for s in students:
        if s['reg_no'] == reg_no:
            s['name'] = data.get('name', s['name'])
            s['course'] = data.get('course', s['course'])
            s['attendance'] = data.get('attendance', s['attendance'])
            if 'grades' in data:
                s['grades'] = data['grades']
                s['cgpa'] = compute_gpa(s['grades'])
            return jsonify({'success': True, 'message': 'Student updated'})
    return jsonify({'error': 'Student not found'}), 404

@app.route('/api/students/<reg_no>', methods=['DELETE'])
def delete_student(reg_no):
    global students
    students = [s for s in students if s['reg_no'] != reg_no]
    return jsonify({'success': True, 'message': 'Student deleted'})

@app.route('/api/students/<reg_no>/profile', methods=['GET'])
def student_profile(reg_no):
    for s in students:
        if s['reg_no'] == reg_no:
            return jsonify(s)
    return jsonify({'error': 'Student not found'}), 404

@app.route('/api/courses', methods=['GET'])
def get_courses():
    return jsonify(courses)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_students': len(students),
        'total_courses': len(courses),
        'avg_cgpa': round(sum(s['cgpa'] for s in students) / len(students), 2) if students else 0
    })

@app.route('/api/recent-students', methods=['GET'])
def get_recent_students():
    recent = students[-5:] if len(students) >= 5 else students
    return jsonify({"recent_students": recent})

@app.route('/api/enrollment-stats', methods=['GET'])
def enrollment_stats():
    stats = []
    for course in courses:
        enrolled_count = len([s for s in students if s['course'] == course['name']])
        stats.append({'course': course['name'], 'enrolled': enrolled_count, 'capacity': 30})
    return jsonify(stats)

@app.route('/api/attendance-summary', methods=['GET'])
def attendance_summary():
    if not students:
        return jsonify({'avg_attendance': 0, 'above_75': 0, 'below_75': 0})
    total = sum(s['attendance'] for s in students)
    avg = round(total / len(students), 2)
    above = len([s for s in students if s['attendance'] >= 75])
    below = len([s for s in students if s['attendance'] < 75])
    return jsonify({'avg_attendance': avg, 'above_75': above, 'below_75': below})
    # ---------- New: Serve additional HTML pages ----------
@app.route('/student/<reg_no>')
def student_page(reg_no):
    return send_from_directory('../frontend', 'student-details.html')

@app.route('/add-student')
def add_student_page():
    return send_from_directory('../frontend', 'add-student.html')

@app.route('/reports')
def reports_page():
    return send_from_directory('../frontend', 'reports.html')

# ---------- New: API for student grades over time (mock) ----------
@app.route('/api/student/<reg_no>/attendance-trend', methods=['GET'])
def attendance_trend(reg_no):
    # Mock monthly attendance data for the student
    return jsonify({'months': ['Jan', 'Feb', 'Mar', 'Apr'], 'attendance': [85, 88, 86, 90]})

# ---------- New: API for overall attendance trend ----------
@app.route('/api/attendance-trend', methods=['GET'])
def overall_attendance_trend():
    return jsonify({'months': ['Jan', 'Feb', 'Mar', 'Apr'], 'avg_attendance': [84, 86, 85, 87]})
@app.route('/all-students')
def all_students():
    return send_from_directory('../frontend', 'all-students.html')

@app.route('/attendance-analytics')
def attendance_analytics():
    return send_from_directory('../frontend', 'attendance-analytics.html')

@app.route('/settings')
def settings():
    return send_from_directory('../frontend', 'settings.html')

@app.route('/edit-student')
def edit_student():
    return send_from_directory('../frontend', 'edit-student.html')
if __name__ == '__main__':
    app.run(debug=True, port=5000)