from celery import Celery
from scripts.request import Request

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequestThread(self, tickets):
    gallicaRequest = Request(tickets, spawnRequestThread.request.id)
    gallicaRequest.start()
    while not (gallicaRequest.isFinished() or gallicaRequest.tooManyRecords):
        self.update_state(
            state="PROGRESS",
            meta={
                'progress': gallicaRequest.getProgressStats()
            })

    if gallicaRequest.tooManyRecords:
        self.update_state(state='TOO_MANY_RECORDS',)
        return{'numTooManyRecords': gallicaRequest.estimateNumRecords}
    else:
        self.update_state(state="SUCCESS")
        return {'progress': 100, 'status': 'Complete!', 'result': 42}
