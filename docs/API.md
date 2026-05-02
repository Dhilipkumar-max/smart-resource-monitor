# API Documentation

## Base URL
`http://localhost:5000/api`

## Endpoints

### 1. **GET /api/system/current**
- **Description**: Returns the latest system-wide resource metrics.
- **Response**:
```json
{
  "timestamp": "2024-02-09T12:00:00",
  "cpu_usage": 45.2,
  "memory_usage": 60.5,
  "available_memory": 8.1
}
```

### 2. **GET /api/apps/current**
- **Description**: Returns a list of currently running applications with their resource usage.
- **Response**:
```json
[
  {
    "app_name": "chrome.exe",
    "pid": 1234,
    "cpu_usage": 15.3,
    "memory_usage": 512.4,
    "timestamp": "2024-02-09T12:00:00"
  },
  ...
]
```

### 3. **GET /api/recommendations**
- **Description**: Generates intelligent recommendations based on current app usage.
- **Response**:
```json
{
  "timestamp": "2024-02-09T12:00:00",
  "recommendations": [
    {
      "app_name": "chrome.exe",
      "severity": "critical",
      "metric": "CPU",
      "value": "52%",
      "reason": "Consuming 52% CPU",
      "suggestion": "Close unused tabs"
    }
  ]
}
```
