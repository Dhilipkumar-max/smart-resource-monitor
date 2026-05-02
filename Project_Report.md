# Smart Resource Monitor: ML-Based System Health Monitoring Using OS Data, DBMS, and Algorithm Analysis

**Expt. No.:** 15  
**Date:** [Insert Date]

---

## 1. PO-PSO Mapping Table

| PO/PSO | PO1 | PO2 | PO3 | PO4 | PO5 | PO6 | PO7 | PO8 | PO9 | PO10 | PO11 | PO12 | PSO1 | PSO2 | PSO3 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Score** | 3 | 3 | 2 | 3 | 3 | 1 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 3 | 2 |

### 1.1 PSO Justification

| PSO | Relevance | Justification |
| :--- | :--- | :--- |
| **PSO1 – Apply fundamental computing knowledge** | 3 | The project applies core programming and system-level concepts to monitor real-time system performance using OS metrics. |
| **PSO2 – Design and implement solutions** | 3 | It integrates database management and machine learning techniques for efficient storage, retrieval, and prediction of system health data. |
| **PSO3 – Use modern tools and technologies** | 2 | It demonstrates full-stack development by integrating frontend visualization with backend APIs and database systems. |

### 1.2 PO Justification

| PO | Relevance | Justification |
| :--- | :--- | :--- |
| **PO1** | 3 | Applies fundamental knowledge of computing, operating systems, and data structures. |
| **PO2** | 3 | Analyzes system metrics to identify performance issues and system health conditions. |
| **PO3** | 2 | Designs a structured system for monitoring and predictive analytics. |
| **PO4** | 3 | Uses analytical thinking and machine learning for prediction and evaluation. |
| **PO5** | 3 | Utilizes modern tools such as Flask, MySQL, Docker, and GitHub. |
| **PO6** | 1 | Demonstrates awareness of system-level environment interactions. |
| **PO7** | 1 | Minimal environmental considerations as it is a software-based system. |
| **PO8** | 1 | Ensures ethical handling of system data without misuse. |
| **PO9** | 2 | Involves collaboration and coordination during development. |
| **PO10** | 2 | Provides effective communication through a user-friendly dashboard. |
| **PO11** | 2 | Handles deployment and resource management using cloud platforms. |
| **PO12** | 2 | Encourages continuous learning in ML, deployment, and system design. |

---

## 2. Introduction

In modern computing environments, monitoring system performance is essential to ensure reliability, efficiency, and stability. Systems often experience performance degradation due to high resource usage, inefficient processes, or unexpected anomalies.

This project introduces a **System Health Monitoring and Prediction System** (Smart Resource Monitor) that continuously collects system metrics and evaluates system health in real time. In addition to monitoring, it leverages machine learning techniques to predict future system conditions, enabling proactive decision-making and issue prevention.

---

## 3. Project Description

The proposed system is designed to monitor key system parameters such as CPU usage, memory utilization, disk usage, and process count. These metrics are collected periodically using operating system-level functions.

The collected data is stored in a normalized relational database structure to ensure efficient data management. A rule-based algorithm evaluates the system health based on predefined thresholds, while a machine learning model predicts future health status.

The system also includes a web-based dashboard that provides:
- Real-time system status
- Historical data visualization
- Health trend analysis
- Machine learning-based predictions

This integration of monitoring, storage, analytics, and visualization results in a comprehensive system for system health management.

---

## 4. System Architecture

*(Insert Architecture Diagram Here)*

---

## 5. Coding Snippets

### 5.1 Frontend (`index.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>System Health Monitor</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<div class="sidebar">
    <h2>System Monitor</h2>
    <button onclick="showSection('live')">Live</button>
    <button onclick="showSection('metrics')">Metrics</button>
    <button onclick="showSection('trends')">Trends</button>
</div>
<div class="main">
    <!-- Live Status -->
    <section id="live">
        <h2>Current Health</h2>
        <p>Status: <span id="health-status">Loading...</span></p>
        <p>CPU: <span id="cpu">0%</span></p>
        <p>Memory: <span id="memory">0%</span></p>
        <p>Disk: <span id="disk">0%</span></p>
    </section>
    <!-- Metrics Table -->
    <section id="metrics" style="display:none;">
        <table id="metrics-table">
            <thead>
                <tr>
                    <th>Time</th><th>CPU</th><th>Memory</th>
                    <th>Disk</th><th>Status</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </section>
    <!-- Graphs -->
    <section id="trends" style="display:none;">
        <canvas id="cpuChart"></canvas>
        <canvas id="memoryChart"></canvas>
    </section>
</div>
<script src="js/main.js"></script>
</body>
</html>
```

### 5.2 Backend (`app.py`)

```python
import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from backend.collectors.os_metrics import collect_metrics
from backend.algorithms.rule_engine import evaluate_system_health
from backend.database.db_operations import insert_metrics, insert_evaluation
from backend.database.db_connection import get_db_connection
from backend.ml.predict import predict_health

app = Flask(__name__)
CORS(app)

# Background Monitoring
def run_monitor():
    while True:
        try:
            metrics = collect_metrics()
            score, status = evaluate_system_health(metrics)
            metric_id = insert_metrics(metrics)
            insert_evaluation(metric_id, score, status)
        except Exception as e:
            print("Error:", e)
        time.sleep(3)

# Latest Health API
@app.route("/api/health/latest")
def get_latest():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM system_health_view
        ORDER BY timestamp DESC LIMIT 1
    """)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(result or {})

# Prediction API
@app.route("/api/health/predict")
def predict():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT cpu_usage, memory_usage, disk_usage,
               process_count, health_score
        FROM system_health_view
        ORDER BY timestamp DESC LIMIT 1
    """)
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    if not data:
        return jsonify({"error": "No data"}), 404
    prediction = predict_health(data)
    return jsonify({
        "predicted_health_status": prediction,
        "input_metrics": data
    })

if __name__ == "__main__":
    threading.Thread(target=run_monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=5000) 
```

---

## 6. GitHub Repository

- **Full Code Link:** [https://github.com/DineshMoorthy007/system-health-monitor](https://github.com/DineshMoorthy007/system-health-monitor)

The repository contains a well-structured implementation of the project, including backend services, frontend interface, database schema, and machine learning components. Version control is maintained effectively, enabling continuous development and deployment.

---

## 7. Screenshots and Visuals

### 7.1 Frontend Structure
**Description:** This picture illustrates the organization of the frontend components, including HTML, CSS, and JavaScript files. The structure follows a modular approach, separating styling, scripting, and layout logic. This improves maintainability, readability, and scalability of the user interface.
*(Insert Image Here)*

### 7.2 Backend Structure
**Description:** This image presents the backend architecture, including modules for data collection, database operations, machine learning, and API handling. The structured separation of components ensures a clean architecture, enabling easy debugging, extension, and maintenance of backend services.
*(Insert Image Here)*

### 7.3 Docker Image for Backend
**Description:** This picture shows the Docker image used for containerizing the backend application. It highlights how the backend is packaged with all dependencies, ensuring consistent execution across environments and simplifying deployment on cloud platforms.
*(Insert Image Here)*

### 7.4 Railway Deployment
**Description:** This image displays the backend service deployed on the Railway platform. It includes details such as deployment status, runtime logs, and the generated public URL. This confirms that the backend is successfully hosted and accessible for API communication.
*(Insert Image Here)*

### 7.5 Database Deployment (MySQL – Railway)
**Description:** This screenshot combines both the database setup and stored data representation. It shows the MySQL database hosted on Railway, including tables and actual system metrics data. The presence of structured records confirms successful data insertion and proper functioning of the data pipeline.
*(Insert Image Here)*

### 7.6 GitHub Pages Deployment
**Description:** This image shows the deployment of the frontend using GitHub Pages. It includes the deployment status and live URL, ensuring that the user interface is publicly accessible and integrated with the backend APIs.
*(Insert Image Here)*

---

## 8. System Output

The following screenshots represent the final output of the system. The dashboard provides a comprehensive view of system performance by displaying real-time metrics, historical data, and graphical trends. It enables users to monitor system health effectively and make informed decisions based on both current and past performance data.

### 8.1 Live Dashboard – System Overview
This screenshot displays real-time system health information, including CPU usage, memory usage, disk utilization, and overall health status. It provides a quick and clear overview of the current system condition.
*(Insert Image Here)*

### 8.2 Historical Metrics Table
This image shows a structured table containing previously recorded system metrics. It allows users to analyze system behavior over time and compare performance values across different timestamps.
*(Insert Image Here)*

### 8.3 Health Trends Visualization
This screenshot presents graphical charts representing system performance trends. Visualization helps in identifying patterns, fluctuations, and potential anomalies in system behavior.
*(Insert Image Here)*

---

## 9. Conclusion

The System Health Monitoring and Prediction System successfully integrates operating system concepts, database management, and machine learning into a unified application. It provides real-time monitoring and predictive insights, enabling proactive system management.

The project demonstrates practical implementation of full-stack development, data analysis, and deployment strategies, making it a comprehensive solution for system monitoring.

---

## 10. Future Work

- The system can be enhanced by incorporating advanced machine learning models such as neural networks or time-series models to improve prediction accuracy.
- Real-time anomaly detection can be added to identify unusual system behaviour and prevent potential performance issues early.
- An alert mechanism can be implemented to notify users through email or notifications when system thresholds are exceeded.
- The system can be extended to support monitoring of multiple machines through a centralized dashboard for better scalability.
- User authentication and role-based access control can be introduced to improve system security and restrict unauthorized access.
- The machine learning model can be periodically retrained using new data to adapt to changing system environments.
