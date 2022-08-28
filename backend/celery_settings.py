import os
import ssl

broker_use_ssl = {
    'ssl_cert_reqs': ssl.CERT_NONE
}
result_backend = os.environ.get('UPSTASH_REDIS_URL', 'redis://localhost:6379/0')
broker_url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')