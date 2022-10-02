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
    responsesForRequestState = {
        'finished': {
            'status': 'Completed'
        },
        'tooManyRecords': {
            'status': 'Too many records!',
            'numRecords': request.estimateNumRecords
        },
        'noRecords': {
            'status': 'No records found!'
        },
        'error': {
            'status': 'Error'
        },
        'addingRecords': {
            'status': 'addingRecords'
        },
        'addingMissingPapers': {
            'status': 'addingMissingPapers'
        },
        'removingDuplicates': {
            'status': 'removingDuplicates'
        }
    }
    while True:
        if responsesForRequestState.get(request.state):
            return responsesForRequestState[request.state]
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': request.getProgressStats()})
            time.sleep(1)

