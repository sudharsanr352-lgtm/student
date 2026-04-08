-- 1. User Authentication [cite: 74]
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- 2. Student Profiles [cite: 74]
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    reg_no VARCHAR(20) UNIQUE,
    cgpa DECIMAL(3,2)
);

-- 3. Academic Records [cite: 74]
CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    credits INT
);

-- 4. Relationships [cite: 74]
CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- 5. Attendance Tracking [cite: 74]
CREATE TABLE attendance (
    student_id INT,
    date DATE,
    status ENUM('Present', 'Absent')
);

-- 6. SCM Audit Log [cite: 74]
CREATE TABLE change_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    changed_by VARCHAR(50),
    change_description TEXT,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);