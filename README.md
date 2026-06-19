# EMSI ClubHub

EMSI ClubHub is a comprehensive Django-based web application designed to manage student clubs, memberships, and events within the EMSI (Ecole Marocaine des Sciences de l'Ingénieur) institution. It streamlines the process of club creation, joining clubs, and organizing events.

## Features

*   **Role-Based Access Control:** Three distinct user roles:
    *   **Student (Etudiant):** Can browse clubs, request to join clubs (up to 3), request to create new clubs, and register for events.
    *   **Club Manager (Responsable de club):** Can manage their assigned club, approve/reject join requests, create event requests, and join up to 2 other clubs.
    *   **Administration:** Has global oversight, approves/rejects club creation requests, and approves/rejects event requests.
*   **Club Management:**
    *   Clubs are categorized (Tech & Innovation, Sports, Arts, Musique, Autre).
    *   Students can submit Club Creation Requests with a logo and description.
    *   Students can send Club Join Requests which must be approved by the club manager.
*   **Event Management:**
    *   Club managers can propose Event Requests specifying date, time, and location (e.g., Amphithéâtre, Salle 12).
    *   Administration approves Event Requests to make them official Events.
    *   Users can register to attend upcoming events.

## Technology Stack

*   **Backend:** Python, Django
*   **Database:** SQLite (default `db.sqlite3` included)
*   **Image Handling:** Pillow (for club logos)

## Prerequisites

*   Python 3.x
*   pip (Python package installer)

## Installation & Setup

1.  **Clone or extract the project repository:**
    Ensure you are in the project root directory (`emsi_clubs_projects`).

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create an administration account (superuser):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

8.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000/`.

## Project Structure

*   `clubs/`: The main Django app containing models, views, and logic for clubs, users, and events.
*   `config/`: The core Django project configuration folder (settings, main urls).
*   `media/`: Directory where uploaded files like club logos are stored.
*   `static/`: Directory for static assets (CSS, JS, images).
*   `templates/`: HTML templates for the frontend.
