# Placement Booster

Placement Booster is a comprehensive platform designed to help students and job seekers prepare for technical and non-technical placements. Built with Flask, this application provides an interactive environment for practicing aptitude, coding, and core concepts.

## Features

- **User Authentication**: Secure sign-up, login, and profile management.
- **Aptitude Tests**: Practice multiple-choice questions across various categories with detailed explanations.
- **Coding Practice**: Solve programming challenges to sharpen technical skills.
- **Progress Tracking**: Keep track of your performance, scores, and daily streaks.
- **Leaderboard**: Compete with other users and track your ranking.
- **Mock Tests**: Full-length mock tests simulating real placement exams.

## Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Security**: Werkzeug (Password Hashing)

## Getting Started

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/darshanpm33/PLACEMENT-BOOSTER.git
   cd PLACEMENT-BOOSTER
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   Run the database setup script to create your tables:
   ```bash
   python migrate_db.py
   ```
   *Optional: Seed the database with sample data using `python seed_data.py`.*

4. **Run the application:**
   ```bash
   python app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000/` or `http://localhost:5000/`.

## License

This project is available for educational and non-commercial use.