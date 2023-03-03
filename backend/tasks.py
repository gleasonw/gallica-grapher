from celery import Celery
import os

app = Celery("tasks", broker=os.environ.get("REDIS_URL"))


@app.task
def add(x, y):
    return x + y
