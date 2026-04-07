from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- DUMMY DATA (Our Fake Database) ---
# This holds all the information for our application.

stats = {'students': 1250, 'faculty': 85, 'courses': 12, 'departments': 5}

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
    {'name': 'Priya Sharma', 'present': 35, 'total': 50, 'percentage': 70}, # Low attendance example
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


# --- PAGE ROUTES ---
# These functions determine what HTML page to load when you click a link.

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', stats=stats)

@app.route('/students')
def students():
    return render_template('students.html', students=students_data)

# --- ACTION ROUTES ---
# These routes don't show a page; they process form data in the background.

@app.route('/add_student', methods=['POST'])
def add_student():
    # 1. Grab the information the user typed into the HTML form
    new_id = request.form.get('id')
    new_name = request.form.get('name')
    new_course = request.form.get('course')
    new_year = request.form.get('year')

    # 2. Package it into a dictionary to match our dummy data format
    new_student = {
        'id': new_id,
        'name': new_name,
        'course': new_course,
        'year': new_year
    }

    # 3. Append the new student to our list
    students_data.append(new_student)
    
    # 4. Update the dashboard statistics counter
    stats['students'] += 1

    # 5. Redirect the browser back to the students page to see the updated list
    return redirect(url_for('students'))

# --- MORE PAGE ROUTES ---

@app.route('/faculty')
def faculty():
    return render_template('faculty.html', faculty=faculty_data)

@app.route('/attendance')
def attendance():
    return render_template('attendance.html', attendance=attendance_data)

@app.route('/marks')
def marks():
    return render_template('marks.html', marks=marks_data)

@app.route('/fees')
def fees():
    return render_template('fees.html', fees=fees_data)

@app.route('/timetable')
def timetable():
    return render_template('timetable.html', timetable=timetable_data)


# --- START THE SERVER ---
if __name__ == '__main__':
    # debug=True automatically restarts the server if you save changes
    app.run(debug=True)