'''
Template of settings
~# cp settings_local.example.py settings_local.py
'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crypto_ocean',
        'USER': '<USER>',
        'PASSWORD': '<PASSWORD>',
        'HOST': 'localhost',
        'PORT': 5432
    }
}

ALLOWED_HOSTS = ['*']


EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
