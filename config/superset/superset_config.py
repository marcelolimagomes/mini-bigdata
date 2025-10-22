import os

# Database
SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin123@postgres:5432/superset'

# Security
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'thisISaSECRET_1234')

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
}

# Cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}
