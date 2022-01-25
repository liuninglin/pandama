from pathlib import Path
LOG_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s|%(name)s|%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'logstash',
            'port': 5001, 
            'version': 1,
            'message_type': 'django', 
            'tags': ['django'],
        },
        'request_logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': Path(LOG_BASE_DIR).resolve().joinpath('logs', 'django_request.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'simple',
        },
        'app_logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': Path(LOG_BASE_DIR).resolve().joinpath('logs', 'django_app.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'simple',
        },
        'celery_logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': Path(LOG_BASE_DIR).resolve().joinpath('logs', 'django_celery.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'simple',
        },
        'elasticapm': {
            'level': 'WARNING',
            'class': 'elasticapm.contrib.django.handlers.LoggingHandler',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery_logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['app_logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
    }
}