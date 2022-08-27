import os

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'NAME': 'gallicagrapher',
            'USER': 'wgleason',
            'PASSWORD': 'ilike2play',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
