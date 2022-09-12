from celery import Celery
from gallica.factory.requestFactory import RequestFactory
import time

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets):
    request = RequestFactory().buildRequest(
        tickets,
        spawnRequest.request.id
    )
    request.start()
    while True:
        if request.finished:
            return {
                'status': 'Complete!',
                'result': 42}
        elif request.tooManyRecords:
            return {
                'status': 'Too many records!',
                'numRecords': request.estimateNumRecords
            }
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': request.getProgressStats()})
            time.sleep(1)


class TooManyRecordsFailure(Exception):
    pass

