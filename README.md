🎉 Festagram – College Event Management System

Festagram is a Flask-based web application designed to simplify college event management.
It enables administrators and students to efficiently manage event details, user participation, and announcements — all in one central platform.

🚀 Features

🔐 User Authentication – Secure login and session handling using Flask-Login.

🗓️ Event Management – Create, update, and delete college event details.

📢 Announcements – Notify users about upcoming events and important updates via email.

📨 Mail Integration – Integrated Flask-Mail for notifications and confirmations.

🧩 Database Integration – SQLite database using SQLAlchemy ORM.

🧠 Modular Architecture – Clean structure for scalability and maintainability.

🧰 Tech Stack
Component	Technology
Frontend	HTML, CSS, Bootstrap (inside /templates and /static)
Backend	Flask (Python)
Database	SQLite (via SQLAlchemy)
Authentication	Flask-Login
Email Service	Flask-Mail
Server Middleware	Werkzeug ProxyFix
⚙️ Installation and Setup

Follow these steps to run Festagram locally:

1️⃣ Clone the Repository
git clone https://github.com/your-username/Festagram.git
cd Festagram

2️⃣ Create a Virtual Environment
python -m venv venv
venv\Scripts\activate   # For Windows
# or
source venv/bin/activate   # For macOS/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Up Environment Variables

Create a .env file or use your terminal to set these (replace with your values):

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=youremail@gmail.com
MAIL_PASSWORD=yourpassword
MAIL_DEFAULT_SENDER=noreply@festagram.edu
SESSION_SECRET=your-secret-key
DATABASE_URL=sqlite:///festagram.db

5️⃣ Run the Application
flask run


or

python app.py


Then open your browser at http://127.0.0.1:5000
