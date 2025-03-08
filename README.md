### SecureTrack - File Integrity Monitoring App

- A real-time File Integrity Monitoring (FIM) tool that tracks file changes in a specified directory and logs created, modified, deleted, or renamed files. Developed with a Python backend and React+Vite frontend and Tailwind along with ShadCN components for styling.

## Features
- Monitor a directory for file changes in real time
- Detect and log file additions, modifications, deletions, and renames
- Store file integrity data in a SQLite database
- Flask-based API for managing monitoring and retrieving logs
- Cross-platform support using watchdog

## Setup and Installation
- Clone the repository
    1. git clone https://github.com/Apex077/SecureTrack_File_Integrity_Monitoring_App
    2. cd SecureTrack_File_Integrity_Monitoring_App
- Set up a Python virtual environment and activate it:
    1. python -m venv venv
    2. .venv\Scripts\activate (Windows)
    3. source .venv/bin/activate (Mac/Linux)
- Install dependencies:
    1. pip install -r requirements.txt

## Running the App:
- Start the Flask Server (After navigating to the Backend Folder)
    1. python log_server.py
- Start the frontend UI (After navigating to the Frontend Folder)
    1. npm install (For dependencies)
    2. npm run dev
