from celery import Celery
from scripts.request import Request
import time
import psutil, os

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets):
    gallicaRequest = Request(tickets, spawnRequest.request.id)
    gallicaRequest.start()
    while True:
        # print how much memory the process is using in MB
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss / 1024 / 1024)
        if gallicaRequest.finished:
            return {
                'status': 'Complete!',
                'result': 42}
        elif gallicaRequest.tooManyRecords:
            return {
                'status': 'Too many records!',
                'numRecords': gallicaRequest.estimateNumRecords
            }
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': gallicaRequest.getProgressStats()})
            time.sleep(1)


class TooManyRecordsFailure(Exception):
    pass

