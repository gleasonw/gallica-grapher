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
    request = factory.buildRequest()
    request.start()
    returnStates = {
        'COMPLETED': {
            'status': 'COMPLETED'
        },
        'TOO_MANY_RECORDS': {
            'status': 'TOO_MANY_RECORDS',
            'numRecords': request.estimateNumRecords
        },
        'NO_RECORDS': {
            'status': 'NO_RECORDS'
        },
        'ERROR': {
            'status': 'ERROR'
        }
    }
    pollStates = {
        'RUNNING': lambda: self.update_state(
            state='PROGRESS',
            meta={'progress': request.getProgressStats()}
        ),
        'ADDING_MISSING_PAPERS': lambda: self.update_state(
            state='ADDING_MISSING_PAPERS'
        ),
        'ADDING_RESULTS': lambda: self.update_state(
            state='ADDING_RESULTS'
        ),
        'REMOVING_DUPLICATES': lambda: self.update_state(
            state='REMOVING_DUPLICATES'
        ),
    }
    while True:
        if response := returnStates.get(request.state):
            return response
        elif pollState := pollStates.get(request.state):
            pollState()
        else:
            print(f"Unknown state: {request.state}")
        time.sleep(1)

