from celery import Celery, states
from scripts.request import Request
from celery.exceptions import Ignore

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequestThread(self, tickets):
    gallicaRequest = Request(tickets, spawnRequestThread.request.id)
    gallicaRequest.start()
    while True:
        if gallicaRequest.tooManyRecords:
            self.update_state(
                state=states.FAILURE,
                meta={'numTooManyRecords': gallicaRequest.estimateNumRecords}
            )
            raise Ignore()
        elif gallicaRequest.isFinished:
            self.update_state(state="SUCCESS")
            return {'status': 'Complete!', 'result': 42}
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': gallicaRequest.getProgressStats()})

