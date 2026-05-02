# User Guide

## Dashboard Overview
The Smart Resource Monitor dashboard provides a real-time view of your system's performance.

### 1. System Metrics
- **CPU Usage**: Real-time graph showing processor utilization percentage.
- **Memory Usage**: Real-time graph showing RAM usage percentage.

### 2. Recommendations Panel
This panel displays intelligent alerts based on resource consumption:
- **Critical Alerts (Red)**: Applications using >50% CPU or >1GB RAM.
- **Warnings (Yellow)**: Applications with elevated usage.
**Action**: Follow the suggestions (e.g., close unused tabs) to improve performance.

### 3. Applications Table
detailed list of all running applications.
- **Search**: type in the search box to find specific apps (e.g., "chrome").
- **Sort**: Use the dropdown to sort by CPU or Memory usage.

## Troubleshooting
- **No Data**: Ensure the Data Collector is running (`python backend/data_collector.py`).
- **Connection Error**: Check if the Backend API is running (`python backend/app.py`).
- **Database Error**: Run `python init_db.py` to reset the database.
