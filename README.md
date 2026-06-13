# Smart College Management System

A web-based MCA final year project built with Python Flask and SQLite.

## Features

- Role based login: Admin, Teacher, Student
- Admin dashboard with total students, teachers, courses and notices
- Student management
- Course management
- Attendance management
- Fees management
- Result management
- Notice board
- Library book management
- Clean responsive UI

## Demo Login

Admin:
- Email: admin@college.com
- Password: admin123

Teacher:
- Email: teacher@college.com
- Password: teacher123

Student:
- Email: student@college.com
- Password: student123

## How to Run on Windows

1. Extract this folder.
2. Open PowerShell in the project folder.
3. Run these commands:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Open browser:

```text
http://127.0.0.1:5000
```

## Project Modules

1. Admin Module
2. Student Module
3. Teacher Module
4. Course Module
5. Attendance Module
6. Fees Module
7. Exam and Result Module
8. Notice Board Module
9. Library Module
10. Authentication Module

## Database

Database file is created automatically here:

```text
instance/college.db
```

## Future Enhancements

- QR code attendance
- Fee receipt PDF generation
- Email/SMS notification
- Student performance prediction using ML
- Chatbot for student help
- Timetable management
- Assignment upload module
