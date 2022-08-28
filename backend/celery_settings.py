import os

result_backend = os.environ.get(
    'REDIS_URL',
    "localhost:6379")
broker_url = os.environ.get(
    'CLOUDAMQP_URL',
    'amqps://ajcbnuig:9K8W9c8J1z1w3f7Js-evF2yMlo_wCLrk@stingray.rmq.cloudamqp.com/ajcbnuig')