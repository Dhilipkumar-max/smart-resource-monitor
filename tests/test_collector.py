import unittest
import sys
import os

# Add relevant paths based on location of THIS file
current_file = os.path.abspath(__file__)
tests_dir = os.path.dirname(current_file)
project_root = os.path.dirname(tests_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now verify imports work
try:
    from backend import data_collector
    from backend import app
    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.path.append(os.path.join(project_root, 'backend'))

# Re-import to be sure
from backend.data_collector import ResourceMonitor
from backend.app import app
from config.config import DB_CONFIG
import psutil
from unittest.mock import Mock, patch

class TestDataCollection(unittest.TestCase):
    
    def setUp(self):
        # Prevent actual database connection during tests
        with patch('mysql.connector.connect') as mock_connect:
            mock_connect.return_value = Mock()
            self.monitor = ResourceMonitor(DB_CONFIG)

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_collect_system_metrics(self, mock_mem, mock_cpu):
        """Test system metrics collection"""
        # Mock psutil responses
        mock_cpu.return_value = 25.5
        mock_mem_obj = Mock()
        mock_mem_obj.percent = 60.0
        mock_mem_obj.available = 8 * (1024**3) # 8GB
        mock_mem.return_value = mock_mem_obj
        
        metrics = self.monitor.collect_system_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['cpu_usage'], 25.5)
        self.assertEqual(metrics['memory_usage'], 60.0)
        self.assertGreater(metrics['available_memory'], 0)
    
    @patch('psutil.process_iter')
    def test_collect_app_metrics(self, mock_process_iter):
        """Test application metrics collection"""
        # Mock process data
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'test_app.exe', 
            'cpu_percent': 10.5,
            'memory_info': Mock(rss=100 * 1024 * 1024) # 100MB
        }
        # Special mocking for cpu_percent method on process object
        mock_proc.cpu_percent.return_value = 10.5
        
        mock_process_iter.return_value = [mock_proc]
        
        apps = self.monitor.collect_app_metrics()
        
        self.assertIsInstance(apps, list)
        if apps:
            self.assertEqual(apps[0]['name'], 'test_app.exe')
            self.assertEqual(apps[0]['cpu_usage'], 10.5)
            self.assertEqual(apps[0]['memory_usage'], 100.0)

if __name__ == '__main__':
    unittest.main()
