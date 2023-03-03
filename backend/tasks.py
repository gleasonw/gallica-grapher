from celery import Celery

app = Celery("tasks", broker="redis://default:j6prqWNEhhw1kUa3uUHW@containers-us-west-68.railway.app:7270")


@app.task
def add(x, y):
    return x + y
