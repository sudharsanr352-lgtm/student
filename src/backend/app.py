from flask import Flask, jsonify, request, render_template, redirect, url_for

app = Flask(__name__, template_folder='../frontend')

# ---------- In‑memory data ----------
students_db = [
    {"reg_no": "2024001", "name": "Alice", "cgpa": 8.5},
    {"reg_no": "2024002", "name": "Bob",   "cgpa": 7.8},
]
stats = {"total_students": 2, "avg_cgpa": 8.15, "active_courses": 5}

# ---------- UI Routes ----------
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/manage-students')
def students_page():
    return render_template('students.html')

# ---------- Authentication ----------
@app.route('/login', methods=['POST'])
def login():
    # Any credentials work for v1.0.0
    return redirect(url_for('dashboard_page'))

# ---------- API Routes ----------
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "app_name": "Student Management System"}), 200

@app.route('/api/students', methods=['GET', 'POST', 'DELETE'])
def students_api():
    if request.method == 'POST':
        data = request.get_json()
        new_student = {
            "reg_no": data.get("reg_no"),
            "name": data.get("name"),
            "cgpa": float(data.get("cgpa", 0))
        }
        students_db.append(new_student)
        # Update stats
        stats["total_students"] = len(students_db)
        stats["avg_cgpa"] = round(sum(s["cgpa"] for s in students_db) / len(students_db), 2)
        return jsonify({"message": "Student created", "student": new_student}), 201

    elif request.method == 'DELETE':
        reg_no = request.args.get('reg_no')
        # Remove student with matching reg_no (modify list in place → no global needed)
        for i, s in enumerate(students_db):
            if s["reg_no"] == reg_no:
                del students_db[i]
                break
        # Update stats
        stats["total_students"] = len(students_db)
        stats["avg_cgpa"] = round(sum(s["cgpa"] for s in students_db) / len(students_db), 2) if students_db else 0
        return jsonify({"message": "Deleted"}), 200

    # GET request
    return jsonify(students_db), 200

@app.route('/api/stats')
def stats_api():
    return jsonify(stats), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)