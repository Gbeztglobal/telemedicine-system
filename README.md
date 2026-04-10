# Telemedicine System for Malaria and Cholera

A comprehensive full-stack Django Web Application built for diagnosing and managing environmentally caused diseases like Malaria and Cholera.

## Features
- **Role-based Auth:** Strict form validation, phone numbers, and profile pictures for Patients and Doctors.
- **JAMB-Style Theme:** Green and white aesthetic, custom Bootstrap 5 user interface.
- **Auto-Diagnosis Engine:** Rule-based AI symptom analysis for diagnosing Malaria and Cholera risks.
- **WebRTC Video Calls:** Real-time peer-to-peer audio and video communication securely signaled over Django Channels WebSockets.
- **Dashboard Management:** Appointments, diagnosis history, and patient directory management.

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### 1. Environment Setup
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Initialisation
Since Django uses SQLite by default:
```bash
python manage.py makemigrations accounts telemedicine chat
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the Server
Because we use Django Channels for WebSocket Signaling (WebRTC), Daphne will automatically run the ASGI server instead of WSGI when using runserver:
```bash
python manage.py runserver
```

### 5. Access
Navigate to `http://localhost:8000/`. You can register a Patient and a Doctor account to test features.

## Video Calling (WebRTC)
The system uses `RTCPeerConnection` for WebRTC communication and Google's public STUN servers to resolve ICE candidates. The call signaling handles Offers, Answers, and ICE candidates using Django Channels (In-Memory Layer for local tests).
