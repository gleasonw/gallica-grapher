import os

result_backend = os.environ.get('UPSTASH_REDIS', 'redis://localhost:6379/0')
broker_url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')