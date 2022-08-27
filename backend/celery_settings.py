import os

broker_url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')