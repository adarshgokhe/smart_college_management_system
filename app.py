from datetime import date, timedelta
from pathlib import Path
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "college.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


DEFAULT_COURSES = [
    ("MCA", "2 Years", "Master of Computer Applications", 25000),
    ("BCA", "3 Years", "Bachelor of Computer Applications", 18000),
    ("B.Tech CSE", "4 Years", "Computer Science and Engineering", 45000),
    ("B.Tech ECE", "4 Years", "Electronics and Communication Engineering", 42000),
    ("B.Tech Civil", "4 Years", "Civil Engineering", 40000),
    ("B.Tech Mechanical", "4 Years", "Mechanical Engineering", 41000),
    ("BBA", "3 Years", "Bachelor of Business Administration", 22000),
    ("MBA", "2 Years", "Master of Business Administration", 52000),
    ("B.Com", "3 Years", "Bachelor of Commerce", 16000),
    ("M.Com", "2 Years", "Master of Commerce", 21000),
    ("B.Sc Computer Science", "3 Years", "Computer Science honors program", 20000),
    ("B.Sc Mathematics", "3 Years", "Mathematics honors program", 17000),
    ("B.Sc Physics", "3 Years", "Physics honors program", 19000),
    ("BA English", "3 Years", "English literature and communication", 15000),
    ("BA Economics", "3 Years", "Economics honors program", 15500),
    ("B.Ed", "2 Years", "Bachelor of Education", 24000),
    ("Diploma IT", "1 Year", "Information Technology diploma", 12000),
    ("PGDCA", "1 Year", "Post Graduate Diploma in Computer Applications", 14000),
]

DEMO_TEACHERS = [
    ("TCH001", "Ravi Teacher", "teacher@college.com", "teacher123", "Computer Science", "9876543210", "Assistant Professor", "M.Tech", "2022-07-01"),
    ("TCH002", "Neha Sharma", "neha.teacher@college.com", "neha123", "Management", "9876543211", "Professor", "MBA", "2021-06-15"),
    ("TCH003", "Amit Verma", "amit.teacher@college.com", "amit123", "Commerce", "9876543212", "Lecturer", "M.Com", "2023-01-10"),
    ("TCH004", "Priya Nair", "priya.teacher@college.com", "priya123", "Mathematics", "9876543213", "Assistant Professor", "M.Sc", "2020-08-12"),
    ("TCH005", "Sanjay Mehta", "sanjay.teacher@college.com", "sanjay123", "Engineering", "9876543214", "Professor", "PhD", "2019-07-20"),
    ("TCH006", "Kavita Rao", "kavita.teacher@college.com", "kavita123", "Humanities", "9876543215", "Lecturer", "MA English", "2024-02-05"),
]

DEMO_STUDENTS = [
    ("ENR2026001", "Adarsh Student", "student@college.com", "student123", "MCA", "1", "9999999999", "India", "Male", "Suresh Kumar"),
    ("ENR2026002", "Aarav Singh", "aarav.student@college.com", "aarav123", "BCA", "2", "9000000002", "Delhi", "Male", "Raj Singh"),
    ("ENR2026003", "Isha Patel", "isha.student@college.com", "isha123", "B.Tech CSE", "3", "9000000003", "Ahmedabad", "Female", "Mehul Patel"),
    ("ENR2026004", "Rohan Gupta", "rohan.student@college.com", "rohan123", "BBA", "1", "9000000004", "Lucknow", "Male", "Anil Gupta"),
    ("ENR2026005", "Meera Joshi", "meera.student@college.com", "meera123", "MBA", "2", "9000000005", "Pune", "Female", "Nitin Joshi"),
    ("ENR2026006", "Kabir Khan", "kabir.student@college.com", "kabir123", "B.Com", "4", "9000000006", "Bhopal", "Male", "Salim Khan"),
    ("ENR2026007", "Sneha Reddy", "sneha.student@college.com", "sneha123", "B.Sc Computer Science", "2", "9000000007", "Hyderabad", "Female", "Vijay Reddy"),
    ("ENR2026008", "Nikhil Das", "nikhil.student@college.com", "nikhil123", "B.Tech ECE", "5", "9000000008", "Kolkata", "Male", "Subhash Das"),
    ("ENR2026009", "Ananya Bose", "ananya.student@college.com", "ananya123", "BA English", "1", "9000000009", "Kolkata", "Female", "Arun Bose"),
    ("ENR2026010", "Dev Malhotra", "dev.student@college.com", "dev123", "B.Sc Mathematics", "3", "9000000010", "Jaipur", "Male", "Vikas Malhotra"),
]

SUBJECTS = [
    ("Programming in Python", "BCA", "TCH001", "1"),
    ("Database Management", "BCA", "TCH001", "2"),
    ("Machine Learning", "MCA", "TCH001", "1"),
    ("Software Engineering", "MCA", "TCH005", "2"),
    ("Data Structures", "B.Tech CSE", "TCH005", "3"),
    ("Digital Electronics", "B.Tech ECE", "TCH005", "2"),
    ("Business Accounting", "B.Com", "TCH003", "1"),
    ("Financial Management", "MBA", "TCH002", "2"),
    ("Marketing Management", "BBA", "TCH002", "1"),
    ("Calculus", "B.Sc Mathematics", "TCH004", "1"),
    ("English Literature", "BA English", "TCH006", "1"),
]

BOOKS = [
    ("Python Programming", "Corey Schafer", "PY-101", 5),
    ("Clean Code", "Robert C. Martin", "CS-102", 4),
    ("Database System Concepts", "Silberschatz", "DB-201", 6),
    ("Operating System Concepts", "Galvin", "OS-301", 5),
    ("Computer Networks", "Tanenbaum", "CN-401", 4),
    ("Principles of Management", "Koontz", "MG-101", 7),
    ("Financial Accounting", "T. S. Grewal", "AC-110", 8),
    ("Engineering Mathematics", "B. S. Grewal", "MA-210", 5),
    ("Digital Logic Design", "M. Morris Mano", "DL-220", 4),
    ("Marketing Management", "Philip Kotler", "MK-310", 6),
    ("English Grammar and Composition", "Wren and Martin", "EN-101", 8),
    ("Business Economics", "H. L. Ahuja", "EC-150", 5),
]


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn, table, column, definition):
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def course_id(conn, name):
    row = conn.execute("SELECT id FROM courses WHERE name=?", (name,)).fetchone()
    return row["id"] if row else None


def teacher_id(conn, employee_id):
    row = conn.execute("SELECT id FROM teachers WHERE employee_id=?", (employee_id,)).fetchone()
    return row["id"] if row else None


def student_id_for_session(conn):
    row = conn.execute("SELECT id FROM students WHERE user_id=?", (session["user_id"],)).fetchone()
    return row["id"] if row else None


def five_subjects_for_course(conn, course_id_value):
    return conn.execute(
        """SELECT sub.*, c.name course_name, u.name teacher_name FROM subjects sub
           LEFT JOIN courses c ON sub.course_id=c.id
           LEFT JOIN teachers t ON sub.teacher_id=t.id
           LEFT JOIN users u ON t.user_id=u.id
           WHERE sub.course_id=?
           ORDER BY CAST(COALESCE(sub.semester, '1') AS INTEGER), sub.id
           LIMIT 5""",
        (course_id_value,),
    ).fetchall()


def department_for_index(index):
    return ["A", "B", "C", "D"][index % 4]


def upsert_credential(conn, user_id, login_id, password, role):
    exists = conn.execute("SELECT id FROM user_credentials WHERE user_id=?", (user_id,)).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO user_credentials(user_id,login_id,password_hint,role) VALUES(?,?,?,?)",
            (user_id, login_id, password, role),
        )


def create_user(conn, name, email, password, role, login_id):
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if user:
        upsert_credential(conn, user["id"], login_id, password, role)
        return user["id"]
    cur = conn.execute(
        "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
        (name, email, generate_password_hash(password), role),
    )
    user_id = cur.lastrowid
    upsert_credential(conn, user_id, login_id, password, role)
    return user_id


def seed_data(conn):
    for name, duration, description, fee_amount in DEFAULT_COURSES:
        row = conn.execute("SELECT id, fee_amount FROM courses WHERE name=?", (name,)).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO courses(name,duration,description,fee_amount) VALUES(?,?,?,?)",
                (name, duration, description, fee_amount),
            )
        elif not row["fee_amount"]:
            conn.execute("UPDATE courses SET fee_amount=? WHERE id=?", (fee_amount, row["id"]))

    admin_id = create_user(conn, "Admin", "admin@college.com", "admin123", "admin", "admin@college.com")

    for employee_id, name, email, password, department, phone, designation, qualification, joining_date in DEMO_TEACHERS:
        user_id = create_user(conn, name, email, password, "teacher", employee_id)
        row = conn.execute("SELECT id FROM teachers WHERE employee_id=? OR user_id=?", (employee_id, user_id)).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO teachers(user_id,employee_id,department,phone,designation,qualification,joining_date) VALUES(?,?,?,?,?,?,?)",
                (user_id, employee_id, department, phone, designation, qualification, joining_date),
            )
        else:
            conn.execute(
                """UPDATE teachers SET employee_id=?, department=?, phone=?, designation=?, qualification=?, joining_date=?
                   WHERE id=?""",
                (employee_id, department, phone, designation, qualification, joining_date, row["id"]),
            )

    for enrollment_no, name, email, password, course_name, semester, phone, address, gender, guardian in DEMO_STUDENTS:
        student_index = int(enrollment_no[-1]) if enrollment_no[-1].isdigit() else 1
        user_id = create_user(conn, name, email, password, "student", enrollment_no)
        c_id = course_id(conn, course_name)
        row = conn.execute("SELECT id FROM students WHERE enrollment_no=? OR user_id=?", (enrollment_no, user_id)).fetchone()
        if not row:
            cur = conn.execute(
                """INSERT INTO students(user_id,enrollment_no,roll_no,course_id,semester,phone,address,gender,guardian_name,
                   dob,admission_date,admission_status,previous_qualification,department)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (user_id, enrollment_no, enrollment_no, c_id, semester, phone, address, gender, guardian, "2004-01-01", str(date.today()), "Approved", "12th Pass", department_for_index(student_index - 1)),
            )
            s_id = cur.lastrowid
            fee = conn.execute("SELECT fee_amount FROM courses WHERE id=?", (c_id,)).fetchone()["fee_amount"]
            conn.execute(
                "INSERT INTO fees(student_id,amount,status,due_date,fee_type,remarks) VALUES(?,?,?,?,?,?)",
                (s_id, fee, "Unpaid", str(date.today() + timedelta(days=30)), "College Fee", "Auto generated admission fee"),
            )
            conn.execute(
                "INSERT INTO fees(student_id,amount,status,due_date,fee_type,remarks) VALUES(?,?,?,?,?,?)",
                (s_id, 1500, "Unpaid", str(date.today() + timedelta(days=45)), "Exam Fee", "Semester exam fee"),
            )
        else:
            conn.execute(
                """UPDATE students SET enrollment_no=?, roll_no=?, course_id=?, semester=?, phone=?, address=?, gender=?,
                   guardian_name=?, admission_status=COALESCE(admission_status, 'Approved'),
                   previous_qualification=COALESCE(previous_qualification, '12th Pass'),
                   department=COALESCE(department, ?)
                   WHERE id=?""",
                (enrollment_no, enrollment_no, c_id, semester, phone, address, gender, guardian, department_for_index(student_index - 1), row["id"]),
            )

    for subject_name, course_name, emp_id, semester in SUBJECTS:
        c_id = course_id(conn, course_name)
        t_id = teacher_id(conn, emp_id)
        exists = conn.execute("SELECT id FROM subjects WHERE name=? AND course_id=?", (subject_name, c_id)).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO subjects(name,course_id,teacher_id,semester) VALUES(?,?,?,?)",
                (subject_name, c_id, t_id, semester),
            )

    subject_templates = [
        "Fundamentals",
        "Practical Lab",
        "Advanced Concepts",
        "Project Work",
        "Professional Skills",
    ]
    teachers = conn.execute("SELECT id FROM teachers ORDER BY id").fetchall()
    courses = conn.execute("SELECT id, name FROM courses ORDER BY id").fetchall()
    for course_index, course in enumerate(courses):
        existing_count = conn.execute("SELECT COUNT(*) c FROM subjects WHERE course_id=?", (course["id"],)).fetchone()["c"]
        if existing_count >= 5:
            continue
        needed = 5 - existing_count
        for subject_index, suffix in enumerate(subject_templates[:needed], start=existing_count + 1):
            subject_name = f"{course['name']} {suffix}"
            exists = conn.execute("SELECT id FROM subjects WHERE name=? AND course_id=?", (subject_name, course["id"])).fetchone()
            if exists:
                continue
            teacher = teachers[(course_index + subject_index) % len(teachers)] if teachers else None
            conn.execute(
                "INSERT INTO subjects(name,course_id,teacher_id,semester) VALUES(?,?,?,?)",
                (subject_name, course["id"], teacher["id"] if teacher else None, str(subject_index)),
            )

    for title, author, isbn, copies in BOOKS:
        exists = conn.execute("SELECT id FROM library_books WHERE isbn=?", (isbn,)).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO library_books(title,author,isbn,total_copies,available_copies) VALUES(?,?,?,?,?)",
                (title, author, isbn, copies, copies),
            )
            book_id = conn.execute("SELECT id FROM library_books WHERE isbn=?", (isbn,)).fetchone()["id"]
            conn.execute(
                "INSERT INTO library_purchases(book_id,vendor,quantity,purchase_date,amount,invoice_no) VALUES(?,?,?,?,?,?)",
                (book_id, "College Book Depot", copies, str(date.today()), copies * 450, f"INV-{isbn}"),
            )

    if not conn.execute("SELECT id FROM notices WHERE title='Welcome'").fetchone():
        conn.execute(
            "INSERT INTO notices(title,message,audience,created_at) VALUES(?,?,?,?)",
            ("Welcome", "Welcome to Smart College Management System", "All", str(date.today())),
        )

    if not conn.execute("SELECT id FROM exams").fetchone():
        for sub in conn.execute("SELECT id, course_id, name FROM subjects LIMIT 8").fetchall():
            conn.execute(
                "INSERT INTO exams(course_id,subject_id,exam_name,exam_date,max_marks,exam_fee,due_date,status) VALUES(?,?,?,?,?,?,?,?)",
                (sub["course_id"], sub["id"], f"{sub['name']} Mid Term", str(date.today() + timedelta(days=20)), 100, 1500, str(date.today() + timedelta(days=10)), "Scheduled"),
            )

    if not conn.execute("SELECT id FROM results").fetchone():
        students = conn.execute("SELECT id, course_id FROM students LIMIT 8").fetchall()
        for idx, student in enumerate(students):
            subject = conn.execute("SELECT id FROM subjects WHERE course_id=? LIMIT 1", (student["course_id"],)).fetchone()
            if subject:
                marks = 68 + (idx * 4) % 28
                grade = "A" if marks >= 80 else "B" if marks >= 65 else "C"
                conn.execute(
                    "INSERT INTO results(student_id,subject_id,marks,max_marks,exam_type,grade,remarks) VALUES(?,?,?,?,?,?,?)",
                    (student["id"], subject["id"], marks, 100, "Mid Term", grade, "Good progress"),
                )

    duplicates = conn.execute(
        "SELECT user_id, MIN(id) keep_id FROM teachers GROUP BY user_id HAVING COUNT(*) > 1"
    ).fetchall()
    for duplicate in duplicates:
        extra_rows = conn.execute(
            "SELECT id FROM teachers WHERE user_id=? AND id<>?",
            (duplicate["user_id"], duplicate["keep_id"]),
        ).fetchall()
        for extra in extra_rows:
            conn.execute("UPDATE subjects SET teacher_id=? WHERE teacher_id=?", (duplicate["keep_id"], extra["id"]))
            conn.execute("DELETE FROM teachers WHERE id=?", (extra["id"],))


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','teacher','student'))
    );
    CREATE TABLE IF NOT EXISTS user_credentials(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        login_id TEXT,
        password_hint TEXT,
        role TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        duration TEXT,
        description TEXT,
        fee_amount REAL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        roll_no TEXT UNIQUE,
        course_id INTEGER,
        semester TEXT,
        phone TEXT,
        address TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    );
    CREATE TABLE IF NOT EXISTS teachers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        department TEXT,
        phone TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        course_id INTEGER,
        teacher_id INTEGER,
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(teacher_id) REFERENCES teachers(id)
    );
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        attendance_date TEXT,
        status TEXT CHECK(status IN ('Present','Absent')),
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    );
    CREATE TABLE IF NOT EXISTS fees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL,
        status TEXT CHECK(status IN ('Paid','Unpaid')),
        due_date TEXT,
        paid_date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );
    CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        marks INTEGER,
        max_marks INTEGER DEFAULT 100,
        exam_type TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    );
    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        audience TEXT DEFAULT 'All',
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS library_books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        isbn TEXT,
        total_copies INTEGER DEFAULT 1,
        available_copies INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS exams(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        subject_id INTEGER,
        exam_name TEXT,
        exam_date TEXT,
        max_marks INTEGER DEFAULT 100,
        exam_fee REAL DEFAULT 0,
        due_date TEXT,
        status TEXT DEFAULT 'Scheduled',
        FOREIGN KEY(course_id) REFERENCES courses(id),
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    );
    CREATE TABLE IF NOT EXISTS library_purchases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        vendor TEXT,
        quantity INTEGER,
        purchase_date TEXT,
        amount REAL,
        invoice_no TEXT,
        FOREIGN KEY(book_id) REFERENCES library_books(id)
    );
    CREATE TABLE IF NOT EXISTS degree_applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        degree_name TEXT,
        specialization TEXT,
        status TEXT DEFAULT 'Applied',
        applied_at TEXT,
        remarks TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );
    """)
    for column, definition in [
        ("fee_amount", "REAL DEFAULT 0"),
    ]:
        ensure_column(conn, "courses", column, definition)
    for column, definition in [
        ("enrollment_no", "TEXT"),
        ("dob", "TEXT"),
        ("gender", "TEXT"),
        ("guardian_name", "TEXT"),
        ("admission_date", "TEXT"),
        ("admission_status", "TEXT DEFAULT 'Approved'"),
        ("previous_qualification", "TEXT"),
        ("department", "TEXT DEFAULT 'A'"),
    ]:
        ensure_column(conn, "students", column, definition)
    for column, definition in [
        ("employee_id", "TEXT"),
        ("designation", "TEXT"),
        ("qualification", "TEXT"),
        ("joining_date", "TEXT"),
    ]:
        ensure_column(conn, "teachers", column, definition)
    for column, definition in [
        ("semester", "TEXT"),
    ]:
        ensure_column(conn, "subjects", column, definition)
    for column, definition in [
        ("fee_type", "TEXT DEFAULT 'College Fee'"),
        ("payment_method", "TEXT"),
        ("receipt_no", "TEXT"),
        ("remarks", "TEXT"),
    ]:
        ensure_column(conn, "fees", column, definition)
    for column, definition in [
        ("grade", "TEXT"),
        ("remarks", "TEXT"),
    ]:
        ensure_column(conn, "results", column, definition)

    seed_data(conn)
    conn.execute("UPDATE students SET enrollment_no=roll_no WHERE enrollment_no IS NULL AND roll_no IS NOT NULL")
    conn.commit()
    conn.close()


def login_required(role=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login"))
            allowed = role if isinstance(role, list) else [role] if role else None
            if allowed and session.get("role") not in allowed:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator


def login_user(user):
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return redirect(url_for("dashboard"))


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html", mode="main")


@app.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND role='admin'", (request.form["login_id"].strip().lower(),)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], request.form["password"]):
            return login_user(user)
        flash("Invalid admin login.", "danger")
    return render_template("login.html", mode="admin")


@app.route("/login/teacher", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        login_id = request.form["login_id"].strip().lower()
        conn = db()
        user = conn.execute(
            """SELECT u.* FROM users u LEFT JOIN teachers t ON t.user_id=u.id
               WHERE u.role='teacher' AND (LOWER(u.email)=? OR LOWER(t.employee_id)=?)""",
            (login_id, login_id),
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], request.form["password"]):
            return login_user(user)
        flash("Invalid teacher login.", "danger")
    return render_template("login.html", mode="teacher")


@app.route("/login/student", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        login_id = request.form["login_id"].strip().lower()
        conn = db()
        user = conn.execute(
            """SELECT u.* FROM users u LEFT JOIN students s ON s.user_id=u.id
               WHERE u.role='student' AND (LOWER(u.email)=? OR LOWER(s.enrollment_no)=?)""",
            (login_id, login_id),
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], request.form["password"]):
            return login_user(user)
        flash("Invalid student login.", "danger")
    return render_template("login.html", mode="student")


@app.route("/login", methods=["POST"])
def legacy_login():
    role = request.form.get("role", "student")
    if role == "admin":
        return admin_login()
    if role == "teacher":
        return teacher_login()
    return student_login()


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required()
def dashboard():
    conn = db()
    counts = {
        "students": conn.execute("SELECT COUNT(*) c FROM students").fetchone()["c"],
        "teachers": conn.execute("SELECT COUNT(*) c FROM teachers").fetchone()["c"],
        "courses": conn.execute("SELECT COUNT(*) c FROM courses").fetchone()["c"],
        "books": conn.execute("SELECT COUNT(*) c FROM library_books").fetchone()["c"],
        "unpaid": conn.execute("SELECT COUNT(*) c FROM fees WHERE status='Unpaid'").fetchone()["c"],
        "paid": conn.execute("SELECT COUNT(*) c FROM fees WHERE status='Paid'").fetchone()["c"],
    }
    notices = conn.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return render_template("dashboard.html", counts=counts, notices=notices)


@app.route("/members")
@login_required("admin")
def members():
    conn = db()
    data = conn.execute(
        """SELECT u.id, u.name, u.email, u.role, uc.login_id, uc.password_hint
           FROM users u LEFT JOIN user_credentials uc ON uc.user_id=u.id
           ORDER BY u.role, u.name"""
    ).fetchall()
    conn.close()
    return render_template("members.html", members=data)


@app.route("/students", methods=["GET", "POST"])
@login_required("admin")
def students():
    conn = db()
    if request.method == "POST":
        password = request.form.get("password") or "student123"
        enrollment_no = request.form["enrollment_no"].strip().upper()
        user_id = create_user(conn, request.form["name"], request.form["email"].lower(), password, "student", enrollment_no)
        cur = conn.execute(
            """INSERT INTO students(user_id,enrollment_no,roll_no,course_id,semester,phone,address,gender,guardian_name,dob,
               admission_date,admission_status,previous_qualification,department)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id, enrollment_no, enrollment_no, request.form["course_id"], request.form["semester"],
                request.form["phone"], request.form["address"], request.form["gender"], request.form["guardian_name"],
                request.form["dob"], request.form["admission_date"], request.form["admission_status"],
                request.form["previous_qualification"], request.form["department"],
            ),
        )
        student_id = cur.lastrowid
        fee = conn.execute("SELECT fee_amount FROM courses WHERE id=?", (request.form["course_id"],)).fetchone()["fee_amount"]
        conn.execute(
            "INSERT INTO fees(student_id,amount,status,due_date,fee_type,remarks) VALUES(?,?,?,?,?,?)",
            (student_id, fee, "Unpaid", str(date.today() + timedelta(days=30)), "College Fee", "Admission fee"),
        )
        conn.commit()
        flash("Student added with enrollment login and college fee.", "success")
    data = conn.execute(
        """SELECT s.*, u.id user_id, u.name, u.email, c.name course_name, c.fee_amount FROM students s
           JOIN users u ON s.user_id=u.id LEFT JOIN courses c ON s.course_id=c.id ORDER BY s.id DESC"""
    ).fetchall()
    courses = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    conn.close()
    return render_template("students.html", students=data, courses=courses)


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required("admin")
def edit_student(student_id):
    conn = db()
    if request.method == "POST":
        conn.execute(
            """UPDATE students SET enrollment_no=?, roll_no=?, course_id=?, semester=?, phone=?, address=?, gender=?,
               guardian_name=?, dob=?, admission_date=?, admission_status=?, previous_qualification=?, department=?
               WHERE id=?""",
            (
                request.form["enrollment_no"], request.form["enrollment_no"], request.form["course_id"],
                request.form["semester"], request.form["phone"], request.form["address"], request.form["gender"],
                request.form["guardian_name"], request.form["dob"], request.form["admission_date"],
                request.form["admission_status"], request.form["previous_qualification"], request.form["department"], student_id,
            ),
        )
        conn.execute(
            "UPDATE users SET name=?, email=? WHERE id=(SELECT user_id FROM students WHERE id=?)",
            (request.form["name"], request.form["email"].lower(), student_id),
        )
        conn.commit()
        conn.close()
        flash("Student details updated.", "success")
        return redirect(url_for("students"))
    student = conn.execute(
        """SELECT s.*, u.name, u.email FROM students s JOIN users u ON s.user_id=u.id WHERE s.id=?""",
        (student_id,),
    ).fetchone()
    courses = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    conn.close()
    return render_template("student_edit.html", student=student, courses=courses)


@app.route("/teachers", methods=["GET", "POST"])
@login_required("admin")
def teachers():
    conn = db()
    if request.method == "POST":
        password = request.form.get("password") or "teacher123"
        employee_id = request.form["employee_id"].strip().upper()
        user_id = create_user(conn, request.form["name"], request.form["email"].lower(), password, "teacher", employee_id)
        conn.execute(
            "INSERT INTO teachers(user_id,employee_id,department,phone,designation,qualification,joining_date) VALUES(?,?,?,?,?,?,?)",
            (user_id, employee_id, request.form["department"], request.form["phone"], request.form["designation"], request.form["qualification"], request.form["joining_date"]),
        )
        conn.commit()
        flash("Teacher added with separate login.", "success")
    data = conn.execute(
        """SELECT t.*, u.id user_id, u.name, u.email FROM teachers t
           JOIN users u ON t.user_id=u.id ORDER BY t.id DESC"""
    ).fetchall()
    conn.close()
    return render_template("teachers.html", teachers=data)


@app.route("/teachers/<int:teacher_id>/edit", methods=["GET", "POST"])
@login_required("admin")
def edit_teacher(teacher_id):
    conn = db()
    if request.method == "POST":
        conn.execute(
            "UPDATE teachers SET employee_id=?, department=?, phone=?, designation=?, qualification=?, joining_date=? WHERE id=?",
            (request.form["employee_id"], request.form["department"], request.form["phone"], request.form["designation"], request.form["qualification"], request.form["joining_date"], teacher_id),
        )
        conn.execute(
            "UPDATE users SET name=?, email=? WHERE id=(SELECT user_id FROM teachers WHERE id=?)",
            (request.form["name"], request.form["email"].lower(), teacher_id),
        )
        conn.commit()
        conn.close()
        flash("Teacher details updated.", "success")
        return redirect(url_for("teachers"))
    teacher = conn.execute(
        "SELECT t.*, u.name, u.email FROM teachers t JOIN users u ON t.user_id=u.id WHERE t.id=?",
        (teacher_id,),
    ).fetchone()
    conn.close()
    return render_template("teacher_edit.html", teacher=teacher)


@app.route("/courses", methods=["GET", "POST"])
@login_required("admin")
def courses():
    conn = db()
    if request.method == "POST":
        conn.execute(
            "INSERT INTO courses(name,duration,description,fee_amount) VALUES(?,?,?,?)",
            (request.form["name"], request.form["duration"], request.form["description"], request.form.get("fee_amount") or 0),
        )
        conn.commit()
        flash("Course added.", "success")
    data = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    conn.close()
    return render_template("courses.html", courses=data)


@app.route("/courses/<int:course_id_value>/edit", methods=["GET", "POST"])
@login_required("admin")
def edit_course(course_id_value):
    conn = db()
    if request.method == "POST":
        conn.execute(
            "UPDATE courses SET name=?, duration=?, fee_amount=?, description=? WHERE id=?",
            (request.form["name"], request.form["duration"], request.form["fee_amount"], request.form["description"], course_id_value),
        )
        conn.commit()
        conn.close()
        flash("Course details updated.", "success")
        return redirect(url_for("courses"))
    course = conn.execute("SELECT * FROM courses WHERE id=?", (course_id_value,)).fetchone()
    conn.close()
    return render_template("course_edit.html", course=course)


@app.route("/subjects", methods=["GET", "POST"])
@login_required()
def subjects():
    conn = db()
    if request.method == "POST" and session.get("role") in ["admin", "teacher"]:
        conn.execute(
            "INSERT INTO subjects(name,course_id,teacher_id,semester) VALUES(?,?,?,?)",
            (request.form["name"], request.form["course_id"], request.form["teacher_id"], request.form["semester"]),
        )
        conn.commit()
        flash("Subject added.", "success")
    if session.get("role") == "student":
        student = conn.execute("SELECT course_id FROM students WHERE id=?", (student_id_for_session(conn),)).fetchone()
        data = five_subjects_for_course(conn, student["course_id"]) if student else []
    else:
        data = []
        for course in conn.execute("SELECT id FROM courses ORDER BY name").fetchall():
            data.extend(five_subjects_for_course(conn, course["id"]))
    courses = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    teachers_data = conn.execute("SELECT t.id, t.employee_id, u.name FROM teachers t JOIN users u ON t.user_id=u.id ORDER BY u.name").fetchall()
    conn.close()
    return render_template("subjects.html", subjects=data, courses=courses, teachers=teachers_data)


@app.route("/admissions", methods=["GET", "POST"])
@login_required()
def admissions():
    conn = db()
    if request.method == "POST" and session.get("role") == "student":
        s_id = student_id_for_session(conn)
        conn.execute(
            "INSERT INTO degree_applications(student_id,degree_name,specialization,status,applied_at,remarks) VALUES(?,?,?,?,?,?)",
            (s_id, request.form["degree_name"], request.form["specialization"], "Applied", str(date.today()), request.form.get("remarks")),
        )
        conn.commit()
        flash("Degree application submitted.", "success")
    if session.get("role") == "student":
        s_id = student_id_for_session(conn)
        applications = conn.execute("SELECT * FROM degree_applications WHERE student_id=? ORDER BY id DESC", (s_id,)).fetchall()
        admissions_data = conn.execute(
            """SELECT s.*, u.name, u.email, c.name course_name FROM students s
               JOIN users u ON s.user_id=u.id LEFT JOIN courses c ON s.course_id=c.id WHERE s.id=?""",
            (s_id,),
        ).fetchall()
    else:
        applications = conn.execute(
            """SELECT da.*, u.name student_name, s.enrollment_no FROM degree_applications da
               JOIN students s ON da.student_id=s.id JOIN users u ON s.user_id=u.id ORDER BY da.id DESC"""
        ).fetchall()
        admissions_data = conn.execute(
            """SELECT s.*, u.name, u.email, c.name course_name FROM students s
               JOIN users u ON s.user_id=u.id LEFT JOIN courses c ON s.course_id=c.id ORDER BY s.id DESC"""
        ).fetchall()
    conn.close()
    return render_template("admissions.html", admissions=admissions_data, applications=applications)


@app.route("/degree-applications/<int:application_id>/status", methods=["POST"])
@login_required("admin")
def update_degree_application(application_id):
    conn = db()
    conn.execute(
        "UPDATE degree_applications SET status=?, remarks=? WHERE id=?",
        (request.form["status"], request.form.get("remarks"), application_id),
    )
    conn.commit()
    conn.close()
    flash("Degree application status updated.", "success")
    return redirect(url_for("admissions"))


@app.route("/attendance", methods=["GET", "POST"])
@login_required()
def attendance():
    conn = db()
    if request.method == "POST" and session.get("role") in ["admin", "teacher"]:
        conn.execute(
            "INSERT INTO attendance(student_id,subject_id,attendance_date,status) VALUES(?,?,?,?)",
            (request.form["student_id"], request.form["subject_id"], request.form["attendance_date"], request.form["status"]),
        )
        conn.commit()
        flash("Attendance saved.", "success")
    where = ""
    params = ()
    if session.get("role") == "student":
        where = "WHERE s.id=?"
        params = (student_id_for_session(conn),)
    data = conn.execute(
        f"""SELECT a.*, u.name student_name, s.enrollment_no, sub.name subject_name FROM attendance a
            JOIN students s ON a.student_id=s.id JOIN users u ON s.user_id=u.id
            JOIN subjects sub ON a.subject_id=sub.id {where}
            ORDER BY a.attendance_date DESC, a.id DESC""",
        params,
    ).fetchall()
    students_data = conn.execute("SELECT s.id, s.enrollment_no, u.name FROM students s JOIN users u ON s.user_id=u.id ORDER BY u.name").fetchall()
    subjects_data = conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()
    conn.close()
    return render_template("attendance.html", attendance=data, students=students_data, subjects=subjects_data)


@app.route("/exams", methods=["GET", "POST"])
@login_required()
def exams():
    conn = db()
    if request.method == "POST" and session.get("role") in ["admin", "teacher"]:
        conn.execute(
            "INSERT INTO exams(course_id,subject_id,exam_name,exam_date,max_marks,exam_fee,due_date,status) VALUES(?,?,?,?,?,?,?,?)",
            (
                request.form["course_id"], request.form["subject_id"], request.form["exam_name"],
                request.form["exam_date"], request.form["max_marks"], request.form["exam_fee"],
                request.form["due_date"], request.form["status"],
            ),
        )
        conn.commit()
        flash("Exam details saved.", "success")
    where = ""
    params = ()
    if session.get("role") == "student":
        s_id = student_id_for_session(conn)
        student = conn.execute("SELECT course_id FROM students WHERE id=?", (s_id,)).fetchone()
        where = "WHERE e.course_id=?"
        params = (student["course_id"],)
    data = conn.execute(
        f"""SELECT e.*, c.name course_name, sub.name subject_name FROM exams e
            LEFT JOIN courses c ON e.course_id=c.id
            LEFT JOIN subjects sub ON e.subject_id=sub.id
            {where} ORDER BY e.exam_date DESC""",
        params,
    ).fetchall()
    courses_data = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    subjects_data = conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()
    conn.close()
    return render_template("exams.html", exams=data, courses=courses_data, subjects=subjects_data)


@app.route("/fees", methods=["GET", "POST"])
@login_required()
def fees():
    conn = db()
    if request.method == "POST" and session.get("role") == "admin":
        conn.execute(
            "INSERT INTO fees(student_id,amount,status,due_date,paid_date,fee_type,payment_method,receipt_no,remarks) VALUES(?,?,?,?,?,?,?,?,?)",
            (
                request.form["student_id"], request.form["amount"], request.form["status"], request.form["due_date"],
                request.form.get("paid_date") or None, request.form["fee_type"], request.form.get("payment_method"),
                request.form.get("receipt_no"), request.form.get("remarks"),
            ),
        )
        conn.commit()
        flash("Fee record saved.", "success")
    where = ""
    params = ()
    if session.get("role") == "student":
        where = "WHERE s.id=?"
        params = (student_id_for_session(conn),)
    data = conn.execute(
        f"""SELECT f.*, u.name student_name, s.enrollment_no, c.name course_name FROM fees f
            JOIN students s ON f.student_id=s.id
            JOIN users u ON s.user_id=u.id
            LEFT JOIN courses c ON s.course_id=c.id {where}
            ORDER BY f.due_date DESC, f.id DESC""",
        params,
    ).fetchall()
    students_data = conn.execute("SELECT s.id, s.enrollment_no, u.name FROM students s JOIN users u ON s.user_id=u.id ORDER BY u.name").fetchall()
    conn.close()
    return render_template("fees.html", fees=data, students=students_data)


@app.route("/fees/<int:fee_id>/edit", methods=["GET", "POST"])
@login_required("admin")
def edit_fee(fee_id):
    conn = db()
    if request.method == "POST":
        conn.execute(
            """UPDATE fees SET student_id=?, fee_type=?, amount=?, status=?, due_date=?, paid_date=?,
               payment_method=?, receipt_no=?, remarks=? WHERE id=?""",
            (
                request.form["student_id"], request.form["fee_type"], request.form["amount"], request.form["status"],
                request.form["due_date"], request.form.get("paid_date") or None, request.form.get("payment_method"),
                request.form.get("receipt_no"), request.form.get("remarks"), fee_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Fee details updated.", "success")
        return redirect(url_for("fees"))
    fee = conn.execute("SELECT * FROM fees WHERE id=?", (fee_id,)).fetchone()
    students_data = conn.execute("SELECT s.id, s.enrollment_no, u.name FROM students s JOIN users u ON s.user_id=u.id ORDER BY u.name").fetchall()
    conn.close()
    return render_template("fee_edit.html", fee=fee, students=students_data)


@app.route("/fees/<int:fee_id>/pay", methods=["GET", "POST"])
@login_required("student")
def pay_fee(fee_id):
    conn = db()
    s_id = student_id_for_session(conn)
    fee = conn.execute(
        """SELECT f.*, u.name student_name, s.enrollment_no, c.name course_name FROM fees f
           JOIN students s ON f.student_id=s.id JOIN users u ON s.user_id=u.id
           LEFT JOIN courses c ON s.course_id=c.id
           WHERE f.id=? AND f.student_id=?""",
        (fee_id, s_id),
    ).fetchone()
    if not fee:
        conn.close()
        flash("Fee record not found.", "danger")
        return redirect(url_for("fees"))
    if fee["status"] == "Paid":
        conn.close()
        flash("This fee is already paid.", "success")
        return redirect(url_for("fees"))
    if request.method == "GET":
        conn.close()
        return render_template("pay_fee.html", fee=fee)
    conn.execute(
        "UPDATE fees SET status='Paid', paid_date=?, payment_method=?, receipt_no=?, remarks=? WHERE id=?",
        (
            str(date.today()),
            request.form["payment_method"],
            request.form.get("transaction_id") or f"RCP-{fee_id:05d}",
            f"Paid through student portal. Payer: {request.form.get('payer_name','')}",
            fee_id,
        ),
    )
    conn.commit()
    conn.close()
    flash("Fee paid successfully.", "success")
    return redirect(url_for("fees"))


@app.route("/results", methods=["GET", "POST"])
@login_required()
def results():
    conn = db()
    if request.method == "POST" and session.get("role") in ["admin", "teacher"]:
        marks = int(request.form["marks"])
        max_marks = int(request.form["max_marks"])
        percentage = (marks / max_marks) * 100 if max_marks else 0
        grade = "A+" if percentage >= 90 else "A" if percentage >= 80 else "B" if percentage >= 65 else "C" if percentage >= 50 else "F"
        conn.execute(
            "INSERT INTO results(student_id,subject_id,marks,max_marks,exam_type,grade,remarks) VALUES(?,?,?,?,?,?,?)",
            (request.form["student_id"], request.form["subject_id"], marks, max_marks, request.form["exam_type"], grade, request.form.get("remarks")),
        )
        conn.commit()
        flash("Result saved with grade.", "success")
    where = ""
    params = ()
    if session.get("role") == "student":
        where = "WHERE s.id=?"
        params = (student_id_for_session(conn),)
    data = conn.execute(
        f"""SELECT r.*, u.name student_name, s.enrollment_no, sub.name subject_name FROM results r
            JOIN students s ON r.student_id=s.id JOIN users u ON s.user_id=u.id
            JOIN subjects sub ON r.subject_id=sub.id {where}
            ORDER BY r.id DESC""",
        params,
    ).fetchall()
    students_data = conn.execute("SELECT s.id, s.enrollment_no, u.name FROM students s JOIN users u ON s.user_id=u.id ORDER BY u.name").fetchall()
    subjects_data = conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()
    conn.close()
    return render_template("results.html", results=data, students=students_data, subjects=subjects_data)


@app.route("/notices", methods=["GET", "POST"])
@login_required()
def notices():
    conn = db()
    if request.method == "POST" and session.get("role") == "admin":
        conn.execute(
            "INSERT INTO notices(title,message,audience,created_at) VALUES(?,?,?,?)",
            (request.form["title"], request.form["message"], request.form["audience"], str(date.today())),
        )
        conn.commit()
        flash("Notice published.", "success")
    data = conn.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("notices.html", notices=data)


@app.route("/library", methods=["GET", "POST"])
@login_required()
def library():
    conn = db()
    if request.method == "POST" and session.get("role") == "admin":
        total = int(request.form["total_copies"])
        cur = conn.execute(
            "INSERT INTO library_books(title,author,isbn,total_copies,available_copies) VALUES(?,?,?,?,?)",
            (request.form["title"], request.form["author"], request.form["isbn"], total, total),
        )
        conn.execute(
            "INSERT INTO library_purchases(book_id,vendor,quantity,purchase_date,amount,invoice_no) VALUES(?,?,?,?,?,?)",
            (cur.lastrowid, request.form["vendor"], total, request.form["purchase_date"], request.form["amount"], request.form["invoice_no"]),
        )
        conn.commit()
        flash("Book and purchase details added.", "success")
    books = conn.execute("SELECT * FROM library_books ORDER BY title").fetchall()
    purchases = conn.execute(
        """SELECT lp.*, b.title book_title FROM library_purchases lp
           LEFT JOIN library_books b ON lp.book_id=b.id ORDER BY lp.id DESC"""
    ).fetchall()
    conn.close()
    return render_template("library.html", books=books, purchases=purchases)


if __name__ == "__main__":
    init_db()
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=5000)
