from celery import Celery
from scripts.request import Request
import time

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequestThread(self, tickets):
    gallicaRequest = Request(tickets, spawnRequestThread.request.id)
    gallicaRequest.start()
    while True:
        if gallicaRequest.finished:
            self.update_state(state="SUCCESS")
            return {'status': 'Complete!', 'result': 42}
        elif gallicaRequest.tooManyRecords:
            self.update_state(state="TOO_MANY_RECORDS")
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

