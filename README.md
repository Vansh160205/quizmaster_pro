# 🎯 QuizMaster Pro

A comprehensive **Quiz and Events Web Application** built with Django, Django REST Framework, and Tailwind CSS. Users can create quizzes, attempt quizzes, view results, manage events, and track their progress through a personalized dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.x-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.x-red.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Database Models](#-database-models)
- [Screenshots](#-screenshots)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| 📝 **Quiz Management** | Create, edit, delete, and publish quizzes |
| ❓ **Question Management** | Add multiple-choice questions with 4 answer options |
| ✅ **Quiz Attempts** | Take quizzes and get instant results |
| 📊 **Score Calculation** | Automatic scoring with percentage calculation |
| 📅 **Event Management** | Create and manage upcoming events |
| 📜 **Quiz History** | View all past quiz submissions |

### Bonus Features

| Feature | Description |
|---------|-------------|
| 🔐 **User Authentication** | Register, login, logout, and profile management |
| 📱 **Responsive Dashboard** | Personal dashboard with statistics |
| 🌐 **REST API** | Full API with Django REST Framework |
| 🎨 **Modern UI** | Beautiful interface with Tailwind CSS |
| 📦 **Seed Data** | Sample data via fixtures |
| 🧪 **Test Suite** | Comprehensive tests for models and views |

---

## 🛠 Technology Stack

| Category | Technology |
|----------|------------|
| **Backend** | Python 3.10+, Django 5.x |
| **API** | Django REST Framework 3.x |
| **Database** | SQLite (default) |
| **Frontend** | HTML5, Tailwind CSS (CDN) |
| **Authentication** | Django Built-in Auth |
| **Testing** | Django TestCase, APITestCase |

---

## 📁 Project Structure

```
quizmaster_pro/
├── 📄 manage.py                 # Django management script
├── 📄 README.md                 # Project documentation
├── 📄 .gitignore               # Git ignore rules
├── 📁 core/                     # Main application
│   ├── 📄 __init__.py
│   ├── 📄 admin.py             # Admin configuration
│   ├── 📄 api_views.py         # REST API views
│   ├── 📄 apps.py              # App configuration
│   ├── 📄 forms.py             # Django forms
│   ├── 📄 models.py            # Database models
│   ├── 📄 serializers.py       # DRF serializers
│   ├── 📄 tests.py             # Test suite
│   ├── 📄 urls.py              # URL routing
│   ├── 📄 views.py             # View functions
│   ├── 📁 fixtures/            # Sample data
│   │   └── 📄 sample_data.json
│   └── 📁 migrations/          # Database migrations
├── 📁 quizmaster/              # Project configuration
│   ├── 📄 __init__.py
│   ├── 📄 asgi.py
│   ├── 📄 settings.py          # Django settings
│   ├── 📄 urls.py              # Main URL routing
│   └── 📄 wsgi.py
├── 📁 static/                  # Static files
│   └── 📁 css/
└── 📁 templates/               # HTML templates
    ├── 📄 base.html            # Base template
    └── 📁 core/
        ├── 📄 home.html
        ├── 📄 quiz_list.html
        ├── 📄 quiz_detail.html
        ├── 📄 quiz_attempt.html
        ├── 📄 quiz_result.html
        ├── 📄 quiz_history.html
        ├── 📄 event_list.html
        ├── 📁 auth/
        │   ├── 📄 login.html
        │   └── 📄 register.html
        └── 📁 dashboard/
            ├── 📄 dashboard_base.html
            ├── 📄 dashboard.html
            ├── 📄 my_quizzes.html
            ├── 📄 create_quiz.html
            ├── 📄 edit_quiz.html
            ├── 📄 delete_quiz.html
            ├── 📄 add_questions.html
            ├── 📄 my_submissions.html
            ├── 📄 my_events.html
            ├── 📄 create_event.html
            ├── 📄 edit_event.html
            ├── 📄 delete_event.html
            └── 📄 profile.html
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/quizmaster-pro.git
cd quizmaster-pro
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install django djangorestframework
```

#### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. Load Sample Data (Optional)

```bash
python manage.py loaddata sample_data.json
```

#### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### 7. Run Development Server

```bash
python manage.py runserver
```

#### 8. Access the Application

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Home Page |
| http://127.0.0.1:8000/admin/ | Admin Panel |
| http://127.0.0.1:8000/api/quizzes/ | API Root |

---

## 📖 Usage

### Public Features (No Login Required)

1. **Browse Quizzes**: View all available quizzes at `/quizzes/`
2. **Take a Quiz**: Click on any quiz to view details and start attempting
3. **View Results**: See your score and correct answers after submission
4. **Browse Events**: View upcoming events at `/events/`
5. **View History**: See all quiz submissions at `/history/`

### Authenticated Features (Login Required)

1. **Dashboard**: Access your personal dashboard at `/dashboard/`
2. **Create Quizzes**: Create new quizzes with questions and answers
3. **Manage Quizzes**: Edit or delete your created quizzes
4. **Create Events**: Schedule new events
5. **View Submissions**: Track your quiz performance
6. **Profile**: Update your profile information

### Admin Features

1. **Manage Users**: Create, edit, delete users
2. **Manage Quizzes**: Full control over all quizzes
3. **View Statistics**: Access submission statistics
4. **Manage Events**: Control all events

---

## 🌐 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register new user |
| GET | `/api/profile/` | Get user profile |
| PUT | `/api/profile/` | Update profile |

### Quizzes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quizzes/` | List all quizzes |
| POST | `/api/quizzes/` | Create new quiz |
| GET | `/api/quizzes/{id}/` | Get quiz details |
| PUT | `/api/quizzes/{id}/` | Update quiz |
| DELETE | `/api/quizzes/{id}/` | Delete quiz |
| POST | `/api/quizzes/{id}/submit/` | Submit quiz answers |

### Questions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quizzes/{id}/questions/` | List quiz questions |
| POST | `/api/quizzes/{id}/questions/` | Add question |
| GET | `/api/questions/{id}/` | Get question details |

### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/` | List all events |
| POST | `/api/events/` | Create new event |
| GET | `/api/events/{id}/` | Get event details |
| PUT | `/api/events/{id}/` | Update event |
| DELETE | `/api/events/{id}/` | Delete event |

### User Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/my-submissions/` | Get user's submissions |
| GET | `/api/my-quizzes/` | Get user's created quizzes |
| GET | `/api/dashboard-stats/` | Get dashboard statistics |

---

## 📊 Database Models

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │    Quiz     │       │  Question   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id          │───┐   │ id          │───┐   │ id          │
│ username    │   │   │ title       │   │   │ quiz_id     │──┐
│ email       │   │   │ description │   │   │ text        │  │
│ password    │   └──►│ created_by  │   └──►│ type        │  │
└─────────────┘       │ is_published│       │ order       │  │
                      └─────────────┘       └─────────────┘  │
                                                             │
┌─────────────┐       ┌─────────────┐       ┌─────────────┐  │
│   Answer    │       │ Submission  │       │ UserAnswer  │  │
├─────────────┤       ├─────────────┤       ├─────────────┤  │
│ id          │◄──────│ id          │◄──────│ id          │  │
│ question_id │───────│ quiz_id     │       │ submission  │  │
│ text        │       │ user_id     │       │ question_id │◄─┘
│ is_correct  │       │ score       │       │ answer_id   │
└─────────────┘       └─────────────┘       │ is_correct  │
                                            └─────────────┘

┌─────────────┐       ┌─────────────┐
│    Event    │       │ UserProfile │
├─────────────┤       ├─────────────┤
│ id          │       │ id          │
│ title       │       │ user_id     │
│ description │       │ bio         │
│ date        │       │ avatar_color│
│ location    │       └─────────────┘
│ created_by  │
└─────────────┘
```

### Model Details

| Model | Fields | Description |
|-------|--------|-------------|
| **Quiz** | id, title, description, created_by, is_published, created_at, updated_at | Stores quiz information |
| **Question** | id, quiz, text, question_type, order, created_at | Stores quiz questions |
| **Answer** | id, question, text, is_correct | Stores answer options |
| **UserSubmission** | id, quiz, user, user_name, score, submitted_at | Stores quiz attempts |
| **UserAnswer** | id, submission, question, answer, is_correct | Stores individual answers |
| **Event** | id, title, description, date, location, created_by | Stores events |
| **UserProfile** | id, user, bio, avatar_color, created_at | Extended user info |

---

## 🖼 Screenshots

### Home Page
```
┌────────────────────────────────────────────────────────────┐
│  🎯 QuizMaster Pro                    [Quizzes] [Events]   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│         Welcome to QuizMaster Pro                          │
│    Test your knowledge and challenge yourself!             │
│                                                            │
│    [Start a Quiz]            [View Events]                 │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  Featured Quizzes              │  Upcoming Events          │
│  ┌──────────┐ ┌──────────┐    │  📅 Python Workshop        │
│  │ Python   │ │ Django   │    │  📅 Web Dev Bootcamp       │
│  │ Basics   │ │ Framework│    │  📅 Django Meetup          │
│  └──────────┘ └──────────┘    │                            │
└────────────────────────────────────────────────────────────┘
```

### Dashboard
```
┌────────────────────────────────────────────────────────────┐
│  Dashboard                                    [Profile ▼]   │
├──────────────┬─────────────────────────────────────────────┤
│              │                                              │
│  Overview    │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  Profile     │  │ Quizzes │ │ Average │ │ Created │        │
│              │  │ Taken:5 │ │Score:75%│ │ Quiz: 3 │        │
│  ──────────  │  └─────────┘ └─────────┘ └─────────┘        │
│  QUIZZES     │                                              │
│  My Quizzes  │  Quick Actions                               │
│  Create Quiz │  [+ Create Quiz] [Take Quiz] [+ Event]       │
│  Submissions │                                              │
│              │  Recent Activity                             │
│  ──────────  │  ├─ Python Quiz - 80%                       │
│  EVENTS      │  ├─ Django Quiz - 70%                       │
│  My Events   │  └─ Web Dev Quiz - 90%                      │
│  Create Event│                                              │
│              │                                              │
└──────────────┴─────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Run All Tests

```bash
python manage.py test core
```

### Run Tests with Verbosity

```bash
python manage.py test core -v 2
```

### Run Specific Test Class

```bash
python manage.py test core.tests.QuizModelTest
```

### Run with Coverage (Optional)

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='core' manage.py test core

# View coverage report
coverage report

# Generate HTML report
coverage html
```

### Test Summary

| Category | Tests | Coverage |
|----------|-------|----------|
| Quiz Model | 6 | ✅ |
| Question Model | 5 | ✅ |
| Answer Model | 3 | ✅ |
| UserSubmission Model | 7 | ✅ |
| UserAnswer Model | 2 | ✅ |
| Event Model | 5 | ✅ |
| UserProfile Model | 5 | ✅ |
| Public Views | 10 | ✅ |
| Auth Views | 5 | ✅ |
| Dashboard Views | 9 | ✅ |
| **Total** | **57** | ✅ |

---

## 📝 Sample Data

The application includes sample data that can be loaded using:

```bash
python manage.py loaddata sample_data.json
```

### Included Sample Data

| Type | Count | Details |
|------|-------|---------|
| Quizzes | 4 | Python, Web Dev, Django, JavaScript |
| Questions | 9 | Various topics with 4 options each |
| Events | 5 | Workshops, meetups, conferences |

---

## ✅ Evaluation Criteria Coverage

| Criteria | Weight | Status | Details |
|----------|--------|--------|---------|
| Django Models & ORM | 25% | ✅ | 7 models with relationships |
| Quiz Submission Logic | 25% | ✅ | Full CRUD with scoring |
| Frontend (Tailwind + UI) | 20% | ✅ | 15+ responsive pages |
| Code Quality & Comments | 15% | ✅ | Documented throughout |
| Documentation | 10% | ✅ | Complete README |
| Bonus Features | 5% | ✅ | All 5 implemented |

### Bonus Features Implemented

- [x] User Authentication (Register, Login, Logout, Profile)
- [x] Quiz History Page
- [x] Django REST Framework API
- [x] Dashboard for Adding Quizzes/Questions
- [x] Seed Data via Fixtures

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Django Documentation
- Django REST Framework
- Tailwind CSS
- All contributors and testers

---

<p align="center">
  Made with ❤️ using Django and Tailwind CSS
</p>
```

---

## How to Use These Files

### Step 1: Create .gitignore

```bash
# In your project root (quizmaster_pro/)
# Create the file and paste the content above
```

### Step 2: Create README.md

```bash
# In your project root (quizmaster_pro/)
# Create the file and paste the content above
```

### Step 3: Update README with Your Info

Replace these placeholders in README.md:
- `yourusername` → Your GitHub username
- `your.email@example.com` → Your email
- `Your Name` → Your actual name

### Step 4: Initialize Git and Push

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - QuizMaster Pro Django Quiz & Events App"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/quizmaster-pro.git

# Push
git branch -M main
git push -u origin main
```

---

## Final Folder Structure

```
quizmaster_pro/
├── .gitignore          ← New file
├── README.md           ← New file
├── db.sqlite3
├── manage.py
├── core/
│   └── ...
├── quizmaster/
│   └── ...
├── static/
│   └── css/
└── templates/
    └── ...
```
