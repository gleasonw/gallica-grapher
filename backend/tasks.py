from celery import Celery
from scripts.requestThread import RequestThread
#TODO: add beat task to delete old DB records
app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequestThread(self, tickets):
    gallicaRequest = RequestThread(tickets)
    gallicaRequest.start()
    while not gallicaRequest.isFinished():
        self.update_state(
            state="PROGRESS",
            meta={
                'progress': gallicaRequest.getProgressStats()
            })
    self.update_state(state="SUCCESS")
    return {'progress': 100, 'status': 'Complete!', 'result': 42}
