from celery import Celery
from gallica.factories.requestFactory import RequestFactory
import time

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets, requestid):
    factory = RequestFactory(
        tickets,
        requestid
    )
    request = factory.build()
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
        elif request.noRecords:
            return {
                'status': 'No records found!',
                'numRecords': 0
            }
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': request.getProgressStats()})
            time.sleep(1)

