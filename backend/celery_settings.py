import os
import ssl

broker_use_ssl = {'ssl_cert_reqs': ssl.CERT_REQUIRED}
redis_backend_use_ssl = {'ssl_cert_reqs': ssl.CERT_REQUIRED}

result_backend = os.environ.get(
    'REDIS_URL',
    "redis://localhost:6379")
broker_url = os.environ.get(
    'REDIS_URL',
    'redis://localhost:6379')
