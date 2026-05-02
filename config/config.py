import os

DB_CONFIG = {
    'host': os.environ.get('MYSQLHOST', '127.0.0.1'),
    'user': os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', 'Anime@121'),
    'database': os.environ.get('MYSQLDATABASE', 'live_resource_monitor'),
    'port': int(os.environ.get('MYSQLPORT', 3306)),
    'pool_name': 'mypool',
    'pool_size': 5
}

API_CONFIG = {
    'host': '0.0.0.0',
    'port': int(os.environ.get('PORT', 5000)),
    'debug': os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
}

COLLECTOR_CONFIG = {
    'interval': 2,
    'log_file': 'collector.log'
}
