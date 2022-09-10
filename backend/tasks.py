from celery import Celery
from request import Request
import time

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets):
    gallicaRequest = Request(tickets, spawnRequest.request.id)
    gallicaRequest.start()
    while True:
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

