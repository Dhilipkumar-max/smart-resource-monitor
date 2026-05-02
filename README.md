# Smart Application Resource Monitoring & Recommendation System

## Project Overview
This project is an intelligent monitoring solution that tracks system and application-level resource usage. It stores data in a MySQL database and visualizes it via a web dashboard, offering intelligent recommendations for resource management.

## Project Structure
```
smart-resource-monitor/
├── config/              # Configuration files
├── database/            # SQL schemas
├── backend/             # Python backend (Collector + API)
│   ├── data_collector.py
│   └── app.py
├── frontend/            # Web interface
│   ├── index.html
│   └── static/
├── requirements.txt     # Python dependencies
└── README.md
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- MySQL Server 8.0+

### 2. Database Setup
Run the initialization script to creating the database and tables automatically:
```bash
python smart-resource-monitor/init_db.py
```

### 3. Installation
```bash
pip install -r requirements.txt
```

### 4. Running the Application
You need to run three components (or two terminals):

**Terminal 1: Data Collector** (runs in background)
```bash
python backend/data_collector.py
```

**Terminal 2: Backend API**
```bash
python backend/app.py
```

**Frontend**
Open `frontend/index.html` directly in your browser, or serve it:
```bash
cd frontend
python -m http.server 8000
```
Then visit `http://localhost:8000`.

## Configuration
Edit `config/config.py` to change database credentials or collection intervals.
