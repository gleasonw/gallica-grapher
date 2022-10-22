from celery import Celery
from gallica.request import Request
import time

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets, requestid):
    request = Request(
        argsBundles=tickets,
        requestID=requestid
    )
    request.start()
    pollStates = {
        'RUNNING': lambda: self.update_state(
            state='RUNNING',
            meta={'progress': request.getProgressStats()}
        ),
        'ADDING_MISSING_PAPERS': lambda: self.update_state(
            state='ADDING_MISSING_PAPERS',
            meta={'progress': request.getProgressStats()}
        ),
        'ADDING_RESULTS': lambda: self.update_state(
            state='ADDING_RESULTS',
            meta={'progress': request.getProgressStats()}
        )
    }
    while True:
        if pollState := pollStates.get(request.state):
            pollState()
        else:
            return {
                'state': request.state,
                'numRecords': request.estimateNumRecords
            }
        time.sleep(1)

