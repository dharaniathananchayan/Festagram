# 🎉 Festagram – College Event Management System

Festagram is a Flask-based web application built to simplify college event coordination and management. It provides a central platform for administrators to create, update, and manage events while keeping students informed through announcements and email notifications. Designed with scalability and modularity in mind, Festagram helps colleges organize fests and campus activities efficiently in a single, easy-to-use system.

🔗 **Live Demo:** [festagram.vercel.app](https://festagram.vercel.app/)

---

## 🚀 Features

- 🔐 **User Authentication** – Secure login and session management using Flask-Login.
- 🗓️ **Event Management** – Create, update, and delete event details.
- 📢 **Announcements** – Send updates and notifications to participants via email.
- 📨 **Mail Integration** – Flask-Mail integration for event confirmations and reminders.
- 🧩 **Database Integration** – SQLite database powered by SQLAlchemy ORM.
- 🧠 **Modular Architecture** – Clean, scalable code structure for easy maintenance and upgrades.

---

## 🧰 Tech Stack

| Layer          | Technology                     |
|----------------|---------------------------------|
| Frontend       | HTML, CSS, Bootstrap            |
| Backend        | Flask (Python)                  |
| Database       | SQLite (SQLAlchemy ORM)         |
| Authentication | Flask-Login                     |
| Email Service  | Flask-Mail                      |
| Middleware     | Werkzeug ProxyFix               |
| Deployment     | Vercel                          |

---

## 🌐 Live Deployment

Festagram is deployed and accessible online at:

👉 **[https://festagram.vercel.app/](https://festagram.vercel.app/)**

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/dharaniathananchayan/Festagram.git
cd Festagram

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root and add the required environment variables:

```env
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///festagram.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password_or_app_password
```

### Run the App

```bash
flask run
```

The app will be available at `http://127.0.0.1:5000/`.

---

## 📁 Project Structure

```
Festagram/
├── app/
│   ├── static/          # CSS, JS, images
│   ├── templates/       # HTML templates
│   ├── models.py        # Database models
│   ├── routes.py        # Application routes
│   └── __init__.py      # App factory / config
├── requirements.txt
├── run.py
└── README.md
```

---

## 👩‍💻 Author

**Dharani Athananchayan**
[GitHub](https://github.com/dharaniathananchayan) · [Live Project](https://festagram.vercel.app/)
