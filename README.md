# AppointmentTracker - Student Advising System

AppointmentTracker is a student advising system designed to facilitate appointment scheduling and tracking between students and advisors.

## Setup Instructions

1. **Download Code:** Clone or download the AppointmentTracker project code from the repository.

2. **Check Python Version:**
    ```bash
    python --version
    ```
    Ensure you have Python installed and verify the version.

3. **Set Up Virtual Environment:** 
   For Windows:
   ```bash
   python -m venv venv

4. **Activate Virtual Environment:**
    ```bash
    venv\Scripts\activate
    ```
   Activate the virtual environment before proceeding.

5. **Install Django in Virtual Environment:**
    ```bash
    pip install django
    ```
   Install Django within the virtual environment.

6. **Make Migrations and Migrate:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
   Create database migrations and apply them to set up the database schema.

7. **Run the Server:**
    ```bash
    python manage.py runserver
    ```
   Launch the Django development server to start the application.

**Note:** Do not delete or modify any other files. Replace "component name" with the appropriate component names as needed.
