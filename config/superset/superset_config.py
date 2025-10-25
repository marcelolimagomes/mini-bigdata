import os
import warnings
from celery.schedules import crontab

# ---------------------------------------------------------
# Suprimir warnings conhecidos
# ---------------------------------------------------------
# pkg_resources está deprecated mas ainda é usado internamente pelo Superset 4.1.4
# Esse warning vem do código interno do Superset (/app/superset/config.py linha 42)
# e não há como evitá-lo sem modificar o código fonte do Superset
warnings.filterwarnings('ignore', message='.*pkg_resources.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pkg_resources')

# ---------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'postgresql://admin:admin123@postgres:5432/superset'

# Evitar avisos do SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ---------------------------------------------------------
# Security & Secret Key
# ---------------------------------------------------------
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'thisISaSECRET_1234')

# JWT Token for async queries (minimum 32 bytes)
GLOBAL_ASYNC_QUERIES_JWT_SECRET = os.environ.get(
    'GLOBAL_ASYNC_QUERIES_JWT_SECRET',
    'thisISaLONGjwtSECRETforASYNCqueries_MUST_BE_32_BYTES_OR_MORE'
)

# Em produção, use uma chave forte e única:
# import secrets
# SECRET_KEY = secrets.token_urlsafe(32)
# GLOBAL_ASYNC_QUERIES_JWT_SECRET = secrets.token_urlsafe(32)

# ---------------------------------------------------------
# CSRF Protection
# ---------------------------------------------------------
# ATENÇÃO: Em produção, mantenha WTF_CSRF_ENABLED = True
# Aqui desabilitado apenas para desenvolvimento/teste local
WTF_CSRF_ENABLED = False  # Desabilita CSRF globalmente (apenas dev/teste)
WTF_CSRF_TIME_LIMIT = None

# Para produção, configure corretamente:
# WTF_CSRF_ENABLED = True
# WTF_CSRF_TIME_LIMIT = 3600

# ---------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "DASHBOARD_VIRTUALIZATION": True,
    "GLOBAL_ASYNC_QUERIES": False,  # Desabilitado para evitar erro do JWT
    "VERSIONED_EXPORT": True,
    "ENABLE_EXPLORE_JSON_CSRF_PROTECTION": False,  # Apenas dev/teste
}

# ---------------------------------------------------------
# Redis & Cache Configuration
# ---------------------------------------------------------
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_CELERY_DB = 0
REDIS_RESULTS_DB = 1
REDIS_CACHE_DB = 2

# Cache para resultados de queries
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_CACHE_DB,
}

# Cache para exploração de dados
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 1 dia
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': REDIS_RESULTS_DB,
}

# ---------------------------------------------------------
# Celery Configuration
# ---------------------------------------------------------


class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}'
    imports = ('superset.sql_lab', 'superset.tasks.scheduler')
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}'
    worker_prefetch_multiplier = 1
    task_acks_late = False
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
    }
    beat_schedule = {
        'reports.scheduler': {
            'task': 'reports.scheduler',
            'schedule': crontab(minute='*', hour='*'),
        },
        'reports.prune_log': {
            'task': 'reports.prune_log',
            'schedule': crontab(minute=0, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

# ---------------------------------------------------------
# Async Query Configuration
# ---------------------------------------------------------
GLOBAL_ASYNC_QUERIES_TRANSPORT = "ws"
GLOBAL_ASYNC_QUERIES_WEBSOCKET_URL = "ws://localhost:8088/"

# ---------------------------------------------------------
# SQL Lab Configuration
# ---------------------------------------------------------
SQLLAB_ASYNC_TIME_LIMIT_SEC = 300  # 5 minutos
SQLLAB_TIMEOUT = 300
SQLLAB_CTAS_NO_LIMIT = True

# Results backend usando Redis (mais estável)
from cachelib.redis import RedisCache

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_RESULTS_DB,
    key_prefix='superset_results_'
)

# ---------------------------------------------------------
# Security & Talisman
# ---------------------------------------------------------
# Talisman habilitado para proteções de segurança
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    "content_security_policy": {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:", "blob:"],
        "worker-src": ["'self'", "blob:"],
        "connect-src": [
            "'self'",
            "https://api.mapbox.com",
            "https://events.mapbox.com",
            "ws://localhost:8088",
            "wss://localhost:8088",
        ],
        "object-src": "'none'",
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    },
    "force_https": False,  # Em produção com HTTPS, mude para True
}

# ---------------------------------------------------------
# Email Configuration (opcional)
# ---------------------------------------------------------
# EMAIL_NOTIFICATIONS = True
# SMTP_HOST = "smtp.gmail.com"
# SMTP_STARTTLS = True
# SMTP_SSL = False
# SMTP_USER = "your-email@gmail.com"
# SMTP_PORT = 587
# SMTP_PASSWORD = "your-app-password"
# SMTP_MAIL_FROM = "your-email@gmail.com"

# ---------------------------------------------------------
# Webdriver Configuration (para alertas/relatórios)
# ---------------------------------------------------------
WEBDRIVER_BASEURL = "http://superset:8088/"
WEBDRIVER_BASEURL_USER_FRIENDLY = "http://localhost:8088/"
WEBDRIVER_TYPE = "chrome"
WEBDRIVER_OPTION_ARGS = [
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]

# ---------------------------------------------------------
# Alert & Report Configuration
# ---------------------------------------------------------
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
ALERT_REPORTS_WORKING_TIME_OUT_KILL = True

# ---------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------
# Configurar Flask-Limiter para usar Redis backend (melhor para produção)
RATELIMIT_ENABLED = True
RATELIMIT_STORAGE_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}"
RATELIMIT_APPLICATION = "100 per second"

# ---------------------------------------------------------
# Row Level Security
# ---------------------------------------------------------
ROW_LEVEL_SECURITY_ENABLED = True

# ---------------------------------------------------------
# Other Configurations
# ---------------------------------------------------------
# Aumenta limite de upload de arquivos
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

# Desabilita exemplos
SUPERSET_LOAD_EXAMPLES = False

# Log level
LOG_LEVEL = "INFO"

# ---------------------------------------------------------
# Custom CSS (opcional)
# ---------------------------------------------------------
# CUSTOM_CSS = """
#     .navbar {
#         background-color: #1f77b4 !important;
#     }
# """
