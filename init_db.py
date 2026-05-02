import mysql.connector
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.config import DB_CONFIG
except ImportError:
    print("Could not import config. Using defaults.")
    DB_CONFIG = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'Anime@121',
        'database': 'live_resource_monitor'
    }

def init_database():
    print(f"Connecting to MySQL at {DB_CONFIG['host']} as {DB_CONFIG['user']}...")
    
    # Connect without database first to create it
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        if not os.path.exists(schema_path):
             # Try adjusting path if running from root
             schema_path = os.path.join('smart-resource-monitor', 'database', 'schema.sql')
        
        print(f"Reading schema from {schema_path}...")
        with open(schema_path, 'r') as f:
            lines = f.readlines()
            
        # Filter comments and join
        clean_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            clean_lines.append(line)
        
        schema_sql = ' '.join(clean_lines)
        commands = schema_sql.split(';')
        
        for cmd in commands:
            cmd = cmd.strip()
            if cmd:
                try:
                    cursor.execute(cmd)
                    print(f"Executed: {cmd[:50]}...")
                except mysql.connector.Error as err:
                    # Ignore common "exists" errors or just print them
                    print(f"Note: {err}")
                        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")
        
    except mysql.connector.Error as err:
        print(f"Failed to connect or initialize: {err}")

if __name__ == "__main__":
    init_database()
