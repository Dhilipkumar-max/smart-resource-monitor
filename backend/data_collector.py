import psutil
import mysql.connector
from datetime import datetime
import time
import logging
import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config import DB_CONFIG, COLLECTOR_CONFIG
except ImportError:
    # Fallback if running directly or config not found
    try:
        from config.config import DB_CONFIG, COLLECTOR_CONFIG
    except ImportError:
        DB_CONFIG = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'Anime@121',
            'database': 'live_resource_monitor'
        }
        COLLECTOR_CONFIG = {'interval': 2}
        print("Warning: Could not import config, using fallback values.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('collector.log'),
        logging.StreamHandler()
    ]
)

class ResourceMonitor:
    def __init__(self, db_config):
        """Initialize database connection"""
        self.db_config = db_config
        self.connection = None
        self.connect_to_database()
    
    def connect_to_database(self):
        """Establish MySQL connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            logging.info("Database connection established")
        except mysql.connector.Error as err:
            logging.error(f"Database connection failed: {err}")
            self.connection = None
    
    def collect_system_metrics(self):
        """Collect system-level resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            metrics = {
                'timestamp': datetime.now(),
                'cpu_usage': round(cpu_percent, 2),
                'memory_usage': round(memory.percent, 2),
                'available_memory': round(memory.available / (1024**3), 2)
            }
            
            logging.info(f"System: CPU={metrics['cpu_usage']}%, Mem={metrics['memory_usage']}%")
            return metrics
        except Exception as e:
            logging.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_app_metrics(self):
        """Collect per-process resource usage"""
        apps = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    pinfo = proc.info
                    
                    # Skip system idle process (pid 0 on Windows)
                    if pinfo['pid'] == 0:
                        continue
                    
                    # CPU usage
                    cpu_usage = proc.cpu_percent(interval=None)
                    
                    # Memory in MB
                    memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    
                    # Store significant processes
                    if cpu_usage > 0.1 or memory_mb > 10:
                        apps.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_usage': round(cpu_usage, 2),
                            'memory_usage': round(memory_mb, 2)
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            logging.info(f"Collected metrics for {len(apps)} apps")
            return apps
        
        except Exception as e:
            logging.error(f"Error collecting app metrics: {e}")
            return []
    
    def save_to_database(self, system_metrics, app_metrics):
        """Persist data to MySQL"""
        if not system_metrics:
            return
        
        # Check connection and reconnect if needed
        if self.connection is None or not self.connection.is_connected():
            self.connect_to_database()
        
        # If still no connection, return early to avoid crash
        if self.connection is None or not self.connection.is_connected():
            return

        cursor = None
        try:
            cursor = self.connection.cursor()
            
            # 1. Insert System Metrics
            sys_query = """
                INSERT INTO system_metrics 
                (timestamp, cpu_usage, memory_usage, available_memory)
                VALUES (%s, %s, %s, %s)
            """
            sys_values = (
                system_metrics['timestamp'],
                system_metrics['cpu_usage'],
                system_metrics['memory_usage'],
                system_metrics['available_memory']
            )
            cursor.execute(sys_query, sys_values)
            system_id = cursor.lastrowid
            
            # 2. Insert App Metrics
            if app_metrics:
                app_query = """
                    INSERT INTO app_metrics 
                    (app_name, pid, cpu_usage, memory_usage, timestamp, system_metric_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # Prepare batch
                app_values = [
                    (
                        app['name'],
                        app['pid'],
                        app['cpu_usage'],
                        app['memory_usage'],
                        system_metrics['timestamp'],
                        system_id
                    )
                    for app in app_metrics
                ]
                cursor.executemany(app_query, app_values)
            
            self.connection.commit()
            logging.info(f"Saved data. System ID: {system_id}")
            
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            if self.connection:
                try:
                    self.connection.rollback()
                except:
                    pass
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def run(self):
        """Main loop"""
        interval = COLLECTOR_CONFIG.get('interval', 2)
        logging.info(f"Starting monitoring (interval: {interval}s)")
        
        try:
            while True:
                sys_metrics = self.collect_system_metrics()
                # We need a small delay or separate thread for accurate per-process cpu_percent if interval is None
                # But here we just sleep at the end. 
                # psutil.cpu_percent(interval=None) returns usage since last call.
                
                app_metrics = self.collect_app_metrics()
                
                self.save_to_database(sys_metrics, app_metrics)
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logging.info("Stopping...")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("DB Connection closed")

if __name__ == "__main__":
    monitor = ResourceMonitor(DB_CONFIG)
    monitor.run()
