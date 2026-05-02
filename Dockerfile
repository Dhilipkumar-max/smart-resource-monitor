FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Railway overrides this with the PORT environment variable)
EXPOSE 5000

# Run the Flask API using Gunicorn
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} backend.app:app
