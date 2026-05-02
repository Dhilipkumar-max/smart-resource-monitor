import unittest
from unittest.mock import Mock, patch
from flask import Flask
import json
import sys
import os

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import app

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('backend.app.get_db_connection')
    def test_health_check(self, mock_db):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    @patch('backend.app.get_db_connection')
    def test_get_system_metrics(self, mock_db):
        """Test system metrics endpoint mock"""
        # Mock database return
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            'timestamp': Mock(isoformat=lambda: "2024-01-01T12:00:00"),
            'cpu_usage': 45.0,
            'memory_usage': 60.0,
            'available_memory': 8.0
        }
        mock_conn = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn

        response = self.app.get('/api/system/current')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['cpu_usage'], 45.0)

if __name__ == '__main__':
    unittest.main()
