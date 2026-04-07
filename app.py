from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from functools import wraps
import sqlite3
import os
import string
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'college-erp-secret-key-2024')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

DATABASE = 'college_erp.db'

def get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_secure_password():
    """Generate a secure default password with uppercase, lowercase, numbers, and symbols."""
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation[:8]  # Limit to common symbols
    
    # Ensure at least one of each type
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(symbols)
    ]
    
    # Fill the rest with random characters from all types
    all_chars = uppercase + lowercase + digits + symbols
    password += [random.choice(all_chars) for _ in range(8)]
    
    # Shuffle to avoid predictability
    random.shuffle(password)
    return ''.join(password)

def init_db():
    """Initialize database with enhanced users table."""
    if os.path.exists(DATABASE):
        # Check if profile_picture column exists, add if needed
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT DEFAULT 'static/images/default-avatar.png'")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.close()
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create enhanced users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            user_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            course TEXT,
            semester INTEGER,
            department TEXT,
            profile_picture TEXT DEFAULT 'static/images/default-avatar.png'
        )
    ''')
    
    # Easy default password for admin
    admin_pass = 'Admin@123'
    
    # Generate secure passwords for faculty and students
    faculty_pass = generate_secure_password()
    student_pass = generate_secure_password()
    
    # Insert demo users
    demo_users = [
        ('admin', admin_pass, 'ADM001', 'Admin User', 'admin', None, None, None, 'static/images/default-avatar.png'),
        ('faculty1', faculty_pass, 'FAC001', 'Dr. Sharma', 'faculty', None, None, 'Computer Science', 'static/images/default-avatar.png'),
        ('student1', student_pass, 'STU001', 'Rahul Kumar', 'student', 'BCA', 4, None, 'static/images/default-avatar.png')
    ]
    
    for user in demo_users:
        try:
            cursor.execute('''
                INSERT INTO users (username, password, user_id, name, role, course, semester, department, profile_picture)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', user)
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    # Print demo user credentials for reference
    print("\n=== DEMO USER CREDENTIALS ===")
    print(f"🔐 Admin     - Username: admin,    Password: {admin_pass}")
    print(f"🔒 Faculty   - Username: faculty1, Password: {faculty_pass}")
    print(f"🔒 Student   - Username: student1, Password: {student_pass}")
    print("=============================\n")
    
    conn.commit()
    conn.close()

def get_user_by_username(username):
    """Get user from database by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_user_login(username, password, role):
    """Verify user credentials from database."""
    user = get_user_by_username(username)
    if user is None:
        return None
    
    if user['password'] != password or user['role'] != role:
        return None
    
    return user

def create_user_in_db(username, name, user_id, role, password=None, **kwargs):
    """Create a new user in the database."""
    if password is None:
        password = generate_secure_password()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password, user_id, name, role, course, semester, department, profile_picture)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            password,
            user_id,
            name,
            role,
            kwargs.get('course'),
            kwargs.get('semester'),
            kwargs.get('department'),
            kwargs.get('profile_picture', 'static/images/default-avatar.png')
        ))
        conn.commit()
        conn.close()
        return True, password
    except sqlite3.IntegrityError as e:
        conn.close()
        return False, str(e)

init_db()
dummy_users = {
    'admin': {
        'password': 'admin123',
        'id': 'ADM001',
        'name': 'Admin User',
        'role': 'admin'
    },
    'faculty1': {
        'password': 'faculty123',
        'id': 'FAC001',
        'name': 'Dr. Sharma',
        'role': 'faculty'
    },
    'student1': {
        'password': 'student123',
        'id': 'STU001',
        'name': 'Rahul Kumar',
        'role': 'student',
        'course': 'BCA',
        'semester': 4
    }
}

stats = {'students': 3, 'faculty': 2, 'courses': 12, 'departments': 5}

students_data = [
    {'id': 'S101', 'name': 'Rahul Kumar', 'course': 'BCA', 'year': '2nd'},
    {'id': 'S102', 'name': 'Priya Sharma', 'course': 'BCA', 'year': '2nd'},
    {'id': 'S103', 'name': 'Amit Singh', 'course': 'BBA', 'year': '1st'}
]

faculty_data = [
    {'id': 'F01', 'name': 'Dr. Sharma', 'department': 'Computer Science'},
    {'id': 'F02', 'name': 'Prof. Verma', 'department': 'Management'}
]

attendance_data = [
    {'name': 'Rahul Kumar', 'present': 45, 'total': 50, 'percentage': 90},
    {'name': 'Priya Sharma', 'present': 35, 'total': 50, 'percentage': 70},
]

marks_data = [
    {'name': 'Rahul Kumar', 'midterm': 38, 'final': 75, 'assignment': 18, 'grade': 'A'},
    {'name': 'Priya Sharma', 'midterm': 30, 'final': 65, 'assignment': 15, 'grade': 'B'},
]

fees_data = [
    {'name': 'Rahul Kumar', 'total': 50000, 'paid': 50000, 'status': 'Paid', 'balance': 0},
    {'name': 'Priya Sharma', 'total': 50000, 'paid': 25000, 'status': 'Partial', 'balance': 25000},
    {'name': 'Amit Singh', 'total': 50000, 'paid': 0, 'status': 'Unpaid', 'balance': 50000},
]

timetable_data = [
    {'day': 'Monday', 'subject': 'Data Structures', 'time': '10:00 AM - 11:30 AM', 'type': 'theory'},
    {'day': 'Tuesday', 'subject': 'Web Development Lab', 'time': '12:00 PM - 02:00 PM', 'type': 'lab'},
    {'day': 'Wednesday', 'subject': 'Database Mgmt', 'time': '10:00 AM - 11:30 AM', 'type': 'theory'},
]


def calculate_grade(midterm, final, assignment):
    """Calculate final grade based on weighted scores."""
    total = (midterm * 0.5) + (final * 0.75) + (assignment * 0.9)
    if total >= 80:
        return 'A'
    elif total >= 70:
        return 'B'
    elif total >= 60:
        return 'C'
    elif total >= 50:
        return 'D'
    else:
        return 'F'

def update_fee_status(fee_record):
    """Update fee payment status based on paid amount."""
    if fee_record['paid'] >= fee_record['total']:
        fee_record['status'] = 'Paid'
        fee_record['balance'] = 0
    elif fee_record['paid'] > 0:
        fee_record['status'] = 'Partial'
        fee_record['balance'] = fee_record['total'] - fee_record['paid']
    else:
        fee_record['status'] = 'Unpaid'
        fee_record['balance'] = fee_record['total']

def find_record_by_name(data_list, name):
    """Find a record in a list by name."""
    for record in data_list:
        if record.get('name') == name:
            return record
    return None

def find_record_by_field(data_list, field, value):
    """Find a record by any field value."""
    for record in data_list:
        if record.get(field) == value:
            return record
    return None

def record_exists(data_list, field, value):
    """Check if a record already exists."""
    return find_record_by_field(data_list, field, value) is not None


def get_admin_dashboard_data():
    """Gather data for admin dashboard."""
    # Calculate total fees collected
    total_fees_collected = sum(fee['paid'] for fee in fees_data)
    
    # Calculate pending fees (outstanding balance)
    pending_fees = sum(fee['balance'] for fee in fees_data if fee['balance'] > 0)
    
    return {
        'user_role': 'admin',
        'total_students': stats['students'],
        'total_faculty': stats['faculty'],
        'total_fees_collected': total_fees_collected,
        'pending_fees': pending_fees,
        'stats': stats
    }

def get_faculty_dashboard_data(username):
    """Gather data for faculty dashboard."""
    # Get faculty details from dummy users
    user_data = dummy_users.get(username, {})
    faculty_name = user_data.get('name', 'Faculty Member')
    
    # For now, use a default department - could be extended to store in database
    faculty_record = find_record_by_name(faculty_data, faculty_name)
    department = faculty_record['department'] if faculty_record else 'Not Assigned'
    
    # Get today's lectures (would need current day - for now, show sample)
    todays_lectures = [c for c in timetable_data if c['type'] == 'theory'][:2]
    
    # Count total students
    total_students = len(students_data)
    
    return {
        'user_role': 'faculty',
        'faculty_name': faculty_name,
        'department': department,
        'todays_lectures': todays_lectures,
        'total_students': total_students,
        'stats': stats
    }

def get_student_dashboard_data(username):
    """Gather data for student dashboard."""
    # Get student details from dummy users
    user_data = dummy_users.get(username, {})
    student_name = user_data.get('name', 'Student')
    course = user_data.get('course', 'Not Assigned')
    semester = user_data.get('semester', 'N/A')
    
    # Get attendance percentage
    attendance_record = find_record_by_name(attendance_data, student_name)
    attendance_percentage = attendance_record['percentage'] if attendance_record else 0
    
    # Get fees status
    fees_record = find_record_by_name(fees_data, student_name)
    fees_status = fees_record['status'] if fees_record else 'Not Found'
    fees_balance = fees_record['balance'] if fees_record else 0
    
    # Get upcoming classes (show all for now - could filter by current/future dates)
    upcoming_classes = timetable_data[:3]
    
    return {
        'user_role': 'student',
        'student_name': student_name,
        'course': course,
        'semester': semester,
        'attendance_percentage': attendance_percentage,
        'fees_status': fees_status,
        'fees_balance': fees_balance,
        'upcoming_classes': upcoming_classes,
        'stats': stats
    }


def filter_attendance_for_student(student_name):
    """Get attendance records for a specific student only."""
    return [record for record in attendance_data if record['name'] == student_name]

def filter_marks_for_student(student_name):
    """Get marks records for a specific student only."""
    return [record for record in marks_data if record['name'] == student_name]

def filter_fees_for_student(student_name):
    """Get fee records for a specific student only."""
    return [record for record in fees_data if record['name'] == student_name]

def role_required(required_role):
    """
    Decorator to protect routes based on user role.
    
    Usage:
        @role_required('admin')
        def route_func():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if user is logged in
            if 'user' not in session:
                flash('Access denied. Please login first.', 'error')
                return redirect(url_for('login'))
            
            # Check if user has required role
            user_role = session['user'].get('role')
            if user_role != required_role:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            
            # User has access - call the original function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'admin')
    
    # Validate username and password exist
    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('login'))
    
    # ONLY accept users from database (no fallback to dummy users)
    user = verify_user_login(username, password, role)
    
    if user is None:
        flash('Invalid username, password, or role. Please check your credentials.', 'error')
        return redirect(url_for('login'))
    
    # Authentication successful - store user in session
    session['user'] = {
        'username': user['username'],
        'role': user['role'],
        'id': user['user_id'],
        'name': user['name'],
        'profile_picture': user['profile_picture']
    }
    
    if user['course']:
        session['user']['course'] = user['course']
    if user['semester']:
        session['user']['semester'] = user['semester']
    if user['department']:
        session['user']['department'] = user['department']
    
    session.modified = True
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    # Clear all session data
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_role = session['user'].get('role')
    username = session['user'].get('username')
    
    # Prepare role-specific data
    if user_role == 'admin':
        dashboard_data = get_admin_dashboard_data()
    elif user_role == 'faculty':
        dashboard_data = get_faculty_dashboard_data(username)
    elif user_role == 'student':
        dashboard_data = get_student_dashboard_data(username)
    else:
        # Fallback for unknown role
        dashboard_data = {'stats': stats, 'user_role': 'unknown'}
    
    # Always include user info
    dashboard_data['user'] = session['user']
    
    return render_template('dashboard.html', **dashboard_data)

@app.route('/profile')
def profile():
    """Display user profile with picture and details."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    return render_template('profile.html', user=user)

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    """Upload profile picture for logged-in user."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if 'profile_picture' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('profile'))
    
    if not allowed_file(file.filename):
        flash('Only PNG, JPG, JPEG, and GIF files are allowed', 'error')
        return redirect(url_for('profile'))
    
    # Save file with secure filename
    filename = secure_filename(f"{session['user']['username']}_profile.{file.filename.rsplit('.', 1)[1].lower()}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Update user profile picture in database
    relative_path = f"static/uploads/{filename}"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET profile_picture = ? WHERE username = ?',
        (relative_path, session['user']['username'])
    )
    conn.commit()
    conn.close()
    
    # Update session
    session['user']['profile_picture'] = relative_path
    session.modified = True
    
    flash('Profile picture uploaded successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/admin/create_user', methods=['GET', 'POST'])
@role_required('admin')
def admin_create_user():
    """Admin creates new admin, faculty, or student users."""
    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        user_id = request.form.get('user_id', '').strip()
        
        if not all([role, username, name, user_id]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin_create_user'))
        
        # Additional fields based on role
        course = request.form.get('course') if role == 'student' else None
        semester = int(request.form.get('semester')) if (role == 'student' and request.form.get('semester')) else None
        department = request.form.get('department') if role == 'faculty' else None
        
        # Create user with secure password
        success, result = create_user_in_db(
            username=username,
            name=name,
            user_id=user_id,
            role=role,
            course=course,
            semester=semester,
            department=department
        )
        
        if success:
            password = result
            flash(f'User created successfully! Username: {username}, Password: {password}', 'success')
            return redirect(url_for('admin_users_list'))
        else:
            flash(f'Error creating user: {result}', 'error')
    
    return render_template('admin_create_user.html')

@app.route('/admin/users')
@role_required('admin')
def admin_users_list():
    """Admin view all users."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, name, user_id, role FROM users ORDER BY role, name')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin_users_list.html', users=users)



@app.route('/students')
def students():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Only admin and faculty can view all students
    user_role = session['user'].get('role')
    if user_role not in ['admin', 'faculty']:
        flash('Access denied. Only admin and faculty can view students.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('students.html', students=students_data)

@app.route('/add_student', methods=['POST'])
@role_required('admin')
def add_student():
    new_id = request.form.get('id')
    new_name = request.form.get('name')
    new_course = request.form.get('course')
    new_year = request.form.get('year')
    
    # Verify all fields are provided
    if not all([new_id, new_name, new_course, new_year]):
        flash('All fields are required', 'error')
        return redirect(url_for('students'))
    
    # Check if student ID already exists
    if record_exists(students_data, 'id', new_id):
        flash('Student ID already exists', 'error')
        return redirect(url_for('students'))
    
    # Create database user account for student
    username = new_id.lower()  # Use student ID as username
    success, result = create_user_in_db(
        username=username,
        name=new_name,
        user_id=new_id,
        role='student',
        course=new_course,
        semester=1  # Default semester
    )
    
    if not success:
        flash(f'Could not create user account: {result}', 'error')
        return redirect(url_for('students'))
    
    password = result
    
    # Add student to students_data
    new_student = {
        'id': new_id,
        'name': new_name,
        'course': new_course,
        'year': new_year
    }
    students_data.append(new_student)
    stats['students'] = len(students_data)
    
    # Initialize attendance, marks, and fees records for new student
    attendance_data.append({
        'name': new_name,
        'present': 0,
        'total': 0,
        'percentage': 0
    })
    
    marks_data.append({
        'name': new_name,
        'midterm': 0,
        'final': 0,
        'assignment': 0,
        'grade': 'N/A'
    })
    
    fees_data.append({
        'name': new_name,
        'total': 50000,
        'paid': 0,
        'status': 'Unpaid',
        'balance': 50000
    })
    
    flash(f'Student created! Username: {username}, Password: {password}', 'success')
    return redirect(url_for('students'))

@app.route('/delete_student/<student_id>', methods=['POST'])
@role_required('admin')
def delete_student(student_id):
    global students_data
    # Remove student from list
    students_data = [s for s in students_data if s['id'] != student_id]
    stats['students'] = len(students_data)
    
    # Also remove from related data structures
    # Find student name to remove from other lists
    student_name = None
    for student in students_data:
        if student['id'] == student_id:
            student_name = student['name']
            break
    
    if student_name:
        attendance_data[:] = [a for a in attendance_data if a['name'] != student_name]
        marks_data[:] = [m for m in marks_data if m['name'] != student_name]
        fees_data[:] = [f for f in fees_data if f['name'] != student_name]
    
    return redirect(url_for('students'))

@app.route('/faculty')
@role_required('admin')
def faculty():
    return render_template('faculty.html', faculty=faculty_data)

@app.route('/add_faculty', methods=['POST'])
@role_required('admin')
def add_faculty():
    faculty_id = request.form.get('id')
    faculty_name = request.form.get('name')
    department = request.form.get('department')
    
    # Verify all fields are provided
    if not all([faculty_id, faculty_name, department]):
        flash('All fields are required', 'error')
        return redirect(url_for('faculty'))
    
    # Check if faculty ID already exists
    if record_exists(faculty_data, 'id', faculty_id):
        flash('Faculty ID already exists', 'error')
        return redirect(url_for('faculty'))
    
    # Create database user account for faculty
    username = faculty_id.lower()  # Use faculty ID as username
    success, result = create_user_in_db(
        username=username,
        name=faculty_name,
        user_id=faculty_id,
        role='faculty',
        department=department
    )
    
    if not success:
        flash(f'Could not create user account: {result}', 'error')
        return redirect(url_for('faculty'))
    
    password = result
    
    # Add new faculty member to faculty_data
    new_faculty = {
        'id': faculty_id,
        'name': faculty_name,
        'department': department
    }
    faculty_data.append(new_faculty)
    stats['faculty'] = len(faculty_data)
    
    flash(f'Faculty created! Username: {username}, Password: {password}', 'success')
    return redirect(url_for('faculty'))

@app.route('/delete_faculty/<faculty_id>', methods=['POST'])
@role_required('admin')
def delete_faculty(faculty_id):
    global faculty_data
    faculty_data = [f for f in faculty_data if f['id'] != faculty_id]
    stats['faculty'] = len(faculty_data)
    return redirect(url_for('faculty'))

@app.route('/attendance')
def attendance():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_role = session['user'].get('role')
    
    # Filter data based on user role
    if user_role == 'student':
        student_name = session['user'].get('name')
        attendance_records = filter_attendance_for_student(student_name)
    else:
        # Admin and Faculty see all records
        attendance_records = attendance_data
    
    # Get list of all students for faculty marking interface
    all_students = students_data
    
    return render_template('attendance.html', attendance=attendance_records, students=all_students)

@app.route('/mark_attendance', methods=['POST'])
@role_required('faculty')
def mark_attendance():
    """Faculty marks attendance for students - present or absent."""
    student_name = request.form.get('student_name')
    status = request.form.get('status')  # 'present' or 'absent'
    
    if not student_name or status not in ['present', 'absent']:
        flash('Invalid attendance data', 'error')
        return redirect(url_for('attendance'))
    
    # Find or create attendance record
    record = find_record_by_name(attendance_data, student_name)
    if record:
        record['total'] += 1
        if status == 'present':
            record['present'] += 1
        # Recalculate percentage
        record['percentage'] = int((record['present'] / record['total']) * 100) if record['total'] > 0 else 0
        flash(f'Attendance marked for {student_name} as {status}', 'success')
    else:
        flash(f'Student {student_name} not found', 'error')
    
    return redirect(url_for('attendance'))

@app.route('/update_attendance', methods=['POST'])
@role_required('faculty')
def update_attendance():
    student_name = request.form.get('name')
    present = int(request.form.get('present', 0))
    total = int(request.form.get('total', 0))
    
    record = find_record_by_name(attendance_data, student_name)
    if record and total > 0:
        record['present'] = min(present, total)
        record['total'] = total
        record['percentage'] = int((record['present'] / record['total']) * 100)
    
    return redirect(url_for('attendance'))

@app.route('/marks')
def marks():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_role = session['user'].get('role')
    
    # Filter data based on user role
    if user_role == 'student':
        student_name = session['user'].get('name')
        marks_records = filter_marks_for_student(student_name)
    else:
        # Admin and Faculty see all records
        marks_records = marks_data
    
    return render_template('marks.html', marks=marks_records)

@app.route('/add_marks', methods=['POST'])
@role_required('faculty')
def add_marks():
    student_name = request.form.get('name')
    midterm = int(request.form.get('midterm', 0))
    final = int(request.form.get('final', 0))
    assignment = int(request.form.get('assignment', 0))
    
    # Find existing marks record
    record = find_record_by_name(marks_data, student_name)
    if record:
        record['midterm'] = midterm
        record['final'] = final
        record['assignment'] = assignment
        record['grade'] = calculate_grade(midterm, final, assignment)
    else:
        # Create new marks record if student exists
        if find_record_by_name(students_data, student_name):
            new_mark = {
                'name': student_name,
                'midterm': midterm,
                'final': final,
                'assignment': assignment,
                'grade': calculate_grade(midterm, final, assignment)
            }
            marks_data.append(new_mark)
    
    return redirect(url_for('marks'))

@app.route('/update_marks/<student_name>', methods=['POST'])
@role_required('faculty')
def update_marks(student_name):
    record = find_record_by_name(marks_data, student_name)
    if record:
        record['midterm'] = int(request.form.get('midterm', record['midterm']))
        record['final'] = int(request.form.get('final', record['final']))
        record['assignment'] = int(request.form.get('assignment', record['assignment']))
        record['grade'] = calculate_grade(record['midterm'], record['final'], record['assignment'])
    
    return redirect(url_for('marks'))

@app.route('/fees')
def fees():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_role = session['user'].get('role')
    
    # Filter data based on user role
    if user_role == 'student':
        student_name = session['user'].get('name')
        fees_records = filter_fees_for_student(student_name)
    else:
        # Admin sees all records
        fees_records = fees_data
    
    return render_template('fees.html', fees=fees_records)

@role_required('admin')
@app.route('/record_payment', methods=['POST'])
def record_payment():
    student_name = request.form.get('name')
    amount = int(request.form.get('amount', 0))
    
    record = find_record_by_name(fees_data, student_name)
    if record and amount > 0:
        record['paid'] += amount
        update_fee_status(record)
    
    return redirect(url_for('fees'))

@role_required('admin')
@app.route('/update_fee_status/<student_name>', methods=['POST'])
def update_fee_status_route(student_name):
    amount_paid = int(request.form.get('paid', 0))
    
    record = find_record_by_name(fees_data, student_name)
    if record:
        record['paid'] = amount_paid
        update_fee_status(record)
    
    return redirect(url_for('fees'))

@app.route('/send_fee_reminder/<student_name>', methods=['POST'])
@role_required('admin')
def send_fee_reminder(student_name):
    # In a real system, this would send an email notification
    # For now, just return to fees page
    return redirect(url_for('fees'))

@app.route('/timetable')
def timetable():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('timetable.html', timetable=timetable_data)

@app.route('/add_class', methods=['POST'])
@role_required('admin')
def add_class():
    day = request.form.get('day')
    subject = request.form.get('subject')
    time_slot = request.form.get('time')
    session_type = request.form.get('type')
    
    # Verify all fields are provided
    if not all([day, subject, time_slot, session_type]):
        return redirect(url_for('timetable'))
    
    # Add new class to timetable
    new_class = {
        'day': day,
        'subject': subject,
        'time': time_slot,
        'type': session_type
    }
    timetable_data.append(new_class)
    
    return redirect(url_for('timetable'))

@app.route('/delete_class/<int:class_index>', methods=['POST'])
@role_required('admin')
def delete_class(class_index):
    global timetable_data
    if 0 <= class_index < len(timetable_data):
        timetable_data.pop(class_index)
    
    return redirect(url_for('timetable'))


if __name__ == '__main__':
    app.run(debug=True)