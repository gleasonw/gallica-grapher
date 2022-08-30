from celery import Celery
from scripts.request import Request

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequestThread(self, tickets):
    gallicaRequest = Request(tickets, self.id)
    gallicaRequest.start()
    while not gallicaRequest.isFinished():
        self.update_state(
            state="PROGRESS",
            meta={
                'progress': gallicaRequest.getProgressStats()
            })
    self.update_state(state="SUCCESS")
    return {'progress': 100, 'status': 'Complete!', 'result': 42}
