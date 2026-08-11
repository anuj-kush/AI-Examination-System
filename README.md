# 🎓 AI-Powered Online Examination System

An AI-powered online examination platform built with **Python and Django**. The system allows students to take online exams, teachers to create and manage exams, and administrators to manage the complete platform.

The project also integrates **Google Gemini AI** to generate multiple-choice questions automatically and provide an AI-powered learning assistant.

---

## 🚀 Features

### 👨‍🎓 Student Module

* Student registration and login
* Student dashboard
* View available courses/exams
* Attempt online examinations
* MCQ-based questions
* Automatic result calculation
* View examination results
* Leaderboard

### 👨‍🏫 Teacher Module

* Teacher registration and login
* Teacher dashboard
* Create and manage courses
* Add examination questions
* View and manage questions
* Generate questions using Gemini AI
* Manage examination content
* View student performance/results

### 🛡️ Admin Module

* Django Admin Panel
* Manage students and teachers
* Manage courses
* Manage questions
* Manage examination results
* Manage users and permissions

### 🤖 AI Features

* AI-generated MCQ questions
* Topic-based question generation
* Gemini API integration
* Automatic JSON-based question processing

### 📊 Examination Features

* Multiple-choice questions
* Automatic evaluation
* Marks calculation
* Result storage
* Student performance tracking
* Leaderboard

---

## 🛠️ Technologies Used

### Backend

* Python
* Django 4.2
* Django ORM
* Django Authentication

### Frontend

* HTML5
* CSS3
* JavaScript


### Database

* SQLite — Local development

### AI

* Google Gemini API

### Machine Learning

* NumPy
* Pandas



### Development Tools

* Git
* GitHub
* VS Code

---

## 🏗️ Project Architecture

```text
User
 │
 ├── Student
 │    ├── Login
 │    ├── Dashboard
 │    ├── Take Exam
 │    ├── Submit Exam
 │    └── View Result
 │
 ├── Teacher
 │    ├── Login
 │    ├── Dashboard
 │    ├── Create Course
 │    ├── Add Questions
 │    └── Generate AI Questions
 │
 └── Admin
      └── Django Admin Panel

```

---

## 🤖 AI Question Generation

Teachers can generate examination questions automatically using Gemini AI.

### Workflow

```text
Teacher
   │
   ▼
Select Course
   │
   ▼
Enter Topic
   │
   ▼
Enter Number of Questions
   │
   ▼
Django creates AI Prompt
   │
   ▼
Gemini API
   │
   ▼
JSON Response
   │
   ▼
Validate & Parse JSON
   │
   ▼
Save Questions to Database
   │
   ▼
Questions Available for Exam
```

Example generated structure:

```json
[
  {
    "question": "What is Django?",
    "option1": "Python Framework",
    "option2": "Database",
    "option3": "Operating System",
    "option4": "Programming Language",
    "answer": "Python Framework"
  }
]
```

---


---

## 🔐 Authentication & Authorization

The project uses Django's built-in authentication system.

Different users have different access levels.

### Student

```text
Student Login
      ↓
Student Dashboard
      ↓
Take Exam
      ↓
View Result
```

### Teacher

```text
Teacher Login
      ↓
Teacher Dashboard
      ↓
Manage Courses
      ↓
Manage Questions
      ↓
Generate AI Questions
```

### Admin

```text
Admin Login
      ↓
Django Admin Panel
      ↓
Manage Entire System
```

Django Groups are used for role management, including the `TEACHER` group.

---

## 🗄️ Database

### Local Development

The project uses SQLite:

```text
db.sqlite3
```

### Production

The application uses PostgreSQL hosted through Neon.

The database is selected using the `DATABASE_URL` environment variable.

```text
Local
    ↓
DATABASE_URL not available
    ↓
SQLite

Production
    ↓
DATABASE_URL available
    ↓
Neon PostgreSQL
```

This allows the same Django project to work with both local SQLite and production PostgreSQL.

---

## ⚙️ Environment Variables

Sensitive information should **never be committed to GitHub**.

Create a `.env` file locally:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=your-postgresql-database-url
```

For production, add these values through the hosting platform's environment-variable settings.

### Important

Do not commit:

```text
.env
```

to GitHub.

Add it to `.gitignore`:

```gitignore
.env
*.pyc
__pycache__/
db.sqlite3
staticfiles/
venv/
.venv/
```

---

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/anuj-kush/AI-Examination-System.git
```

```bash
cd AI-Examination-System
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
GEMINI_API_KEY=your-api-key
```

For local SQLite development, you don't need `DATABASE_URL`.

### 6. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create admin user

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```


```

### Procfile

```text
web: gunicorn exam_site.wsgi
```

### Runtime

The project uses Python 3.11 for deployment:

```text
python-3.11.10
```

### Build Command

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### Start Command

```bash
gunicorn exam_site.wsgi
```

---

## 📁 Project Structure

The project structure may vary depending on the current application organization, but the main Django project follows this pattern:

```text
AI-Examination-System/
│
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .gitignore
│
├── exam/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── predictor.py
│   └── ...
│
├── exam_site/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── db.sqlite3
```

---

## 🔒 Security

The project uses Django security features including:

* Password hashing
* Authentication
* Authorization
* Django ORM
* Production HTTPS configuration


API keys and database credentials are not stored directly in source code.

---

## 🧪 Testing

Run Django system checks:

```bash
python manage.py check
```

Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Run tests:

```bash
python manage.py test
```

---

## 📈 Future Improvements

Possible future improvements include:

* AI-based exam proctoring
* Face recognition
* Real-time student monitoring
* Advanced analytics dashboard
* Email notifications
* Password reset via email
* REST API
* JWT authentication
* Docker deployment
* CI/CD pipeline
* Redis and Celery
* Improved AI Tutor with conversation history
* Automated test coverage

---

## 🎯 Project Objective

The main objective of this project is to provide a complete online examination platform that combines traditional examination management with modern AI capabilities.

It demonstrates practical experience with:

* Python
* Django
* Database management
* REST/API integration
* Authentication
* Role-based authorization
* AI integration
* Cloud deployment
* Git/GitHub

---

## 👨‍💻 Developer

**Anuj Kushwaha**

MCA | Python & Django Developer | AI/ML Enthusiast

### Technologies

```text
Python • Django • SQL • PostgreSQL
REST API • AI/ML • Gemini API
HTML • CSS • Bootstrap • JavaScript
Git • GitHub 
```

---


**Repository:**
https://github.com/anuj-kush/AI-Examination-System
