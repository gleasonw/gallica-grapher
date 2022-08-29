import os

result_backend = os.environ.get(
    'REDIS_URL',
    "redis://localhost:6379")
broker_url = os.environ.get(
    'REDIS_URL',
    'redis://localhost:6379')
