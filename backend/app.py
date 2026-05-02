from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta
import logging
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config import DB_CONFIG, API_CONFIG
except ImportError:
    # Use fallback or dummy config
    print("Warning: Could not import config from config.config")
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'monitor_user',
        'password': 'secure_password',
        'database': 'live_resource_monitor'
    }
    API_CONFIG = {'host': '0.0.0.0', 'port': 5000, 'debug': True}

app = Flask(__name__)
# Enable CORS for all routes (or specific origins)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

from decimal import Decimal

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

@app.route('/api/system/current', methods=['GET'])
def get_current_system_metrics():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            result['timestamp'] = result['timestamp'].isoformat()
            return jsonify(convert_decimals(result))
        return jsonify({"error": "No data"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/history', methods=['GET'])
def get_system_history():
    duration = request.args.get('duration', default=300, type=int)
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM system_metrics WHERE timestamp >= %s ORDER BY timestamp ASC"
        threshold = datetime.now() - timedelta(seconds=duration)
        cursor.execute(query, (threshold,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for r in results:
            r['timestamp'] = r['timestamp'].isoformat()
        
        return jsonify(convert_decimals(results))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/apps/current', methods=['GET'])
def get_current_apps():
    # Only return apps from the LAST system timestamp
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # get max timestamp first
        cursor.execute("SELECT MAX(timestamp) as last_ts FROM system_metrics")
        last_ts = cursor.fetchone()['last_ts']
        
        if not last_ts:
            return jsonify([])
        
        query = """
            SELECT app_name, pid, cpu_usage, memory_usage, timestamp
            FROM app_metrics
            WHERE timestamp = %s
            ORDER BY cpu_usage DESC
        """
        cursor.execute(query, (last_ts,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for r in results:
            r['timestamp'] = r['timestamp'].isoformat()
            
        return jsonify(convert_decimals(results))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get latest apps
        cursor.execute("SELECT MAX(timestamp) as last_ts FROM system_metrics")
        last_ts = cursor.fetchone()['last_ts']
        
        if not last_ts:
            return jsonify({'recommendations': []})
            
        query = "SELECT app_name, cpu_usage, memory_usage FROM app_metrics WHERE timestamp = %s"
        cursor.execute(query, (last_ts,))
        apps = cursor.fetchall()
        cursor.close()
        conn.close()
        
        recs = []
        for app in apps:
            # app values might be decimal, convert for comparison logic just to be safe (though Decimal>int works)
            # but for consistency we use converted values or just rely on python
            cpu = float(app['cpu_usage'])
            mem = float(app['memory_usage'])
            
            if cpu > 50:
                recs.append({
                    'app_name': app['app_name'],
                    'severity': 'critical',
                    'metric': 'CPU',
                    'value': f"{cpu:.1f}%",
                    'reason': f"Consuming {cpu:.1f}% CPU",
                    'suggestion': "Consider closing unused tabs or checking for loops."
                })
            elif cpu > 30:
                recs.append({
                    'app_name': app['app_name'],
                    'severity': 'warning',
                    'metric': 'CPU',
                    'value': f"{cpu:.1f}%",
                    'reason': f"High CPU: {cpu:.1f}%",
                    'suggestion': "Monitor usage."
                })
                
            if mem > 1000: # MB
                 recs.append({
                    'app_name': app['app_name'],
                    'severity': 'critical',
                    'metric': 'Memory',
                    'value': f"{mem:.1f} MB",
                    'reason': f"High Memory: {mem:.1f} MB",
                    'suggestion': "Close unused windows."
                })
        
        return jsonify({'timestamp': datetime.now().isoformat(), 'recommendations': recs})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
