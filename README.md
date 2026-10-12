# Health Tracker

Health Tracker is a personal health management web application built using Python, Flask, and MySQL. It provides a centralized platform for users to manage their health information, track medications, organize appointments, and monitor health metrics.

## Features

- **User Authentication:** User registration and login with password hashing.
- **Dashboard:** Overview of personal health information.
- **Medical Records Management:** Add, view, update, and manage medical records.
- **Medicine Tracking:** Maintain medication schedules and track daily medication status.
- **Appointment Management:** Organize and manage healthcare appointments.
- **Vaccination Tracking:** Maintain vaccination records.
- **Health Metrics:** Record health measurements and visualize trends using charts.
- **Medical Report Management:** Upload, access, and manage medical reports.
- **Profile Management:** View and update personal account information.

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Templating Engine | Jinja2 |
| Database | MySQL |
| Database Connector | MySQL Connector/Python |
| Data Visualization | Chart.js |
| Configuration Management | python-dotenv |

## Project Structure

```text
health-tracker/
├── app.py
├── requirements.txt
├── schema.sql
├── sql/
│   ├── auth.sql
│   ├── dashboard.sql
│   ├── records.sql
│   ├── medicines.sql
│   ├── appointments.sql
│   ├── vaccinations.sql
│   ├── metrics.sql
│   └── profile.sql
├── templates/
├── static/
│   ├── css/
│   └── js/
└── uploads/
```

## Prerequisites

Before running the application, ensure that you have installed:

- Python 3.10 or later
- MySQL Server
- MySQL Workbench (optional, for database management)
- Git

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/meruflin/health-tracker.git
cd health-tracker
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and configure the following variables with your local MySQL credentials:

```env
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=3306
DB_USER=your-mysql-username
DB_PASSWORD=your-mysql-password
DB_NAME=health_tracker
```

Replace the example values with your own configuration. Do not commit the `.env` file or expose database credentials and secret keys publicly.

### 5. Set Up the Database

1. Start your MySQL Server.
2. Open MySQL Workbench and connect to your local server.
3. Execute the SQL statements in `schema.sql` to create the database and required tables.

Ensure that the database name and credentials match your `.env` configuration.

### 6. Run the Application

Start the Flask development server:

```bash
python app.py
```

Open the following URL in your browser:

http://127.0.0.1:5000

## Security and Privacy

- Passwords should be stored using an appropriate password-hashing algorithm.
- Database credentials and application secret keys must be kept outside version control.
- Uploaded medical reports and personal health information should not be committed to a public repository.
- The Flask development server is intended for local development, not production deployment.

## Future Improvements

- Deploy the application to a production hosting platform.
- Add automated testing and validation.
- Improve accessibility and responsive design.
- Introduce additional health analytics and reporting capabilities.

## Author

**Meruflin Jeeva**

GitHub: [meruflin](https://github.com/meruflin)

## License

No license has been specified yet. All rights are reserved unless a license is added to this repository.
