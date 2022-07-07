from celery import Celery
import time
from requestThread import RequestThread

celery = Celery(
    'api.tasks',
    broker='amqp://',
    backend='redis://localhost')


@celery.task(bind=True)
def spawnRequestThread(self, tickets):
    gallicaRequest = RequestThread(tickets)
    gallicaRequest.start()
    while gallicaRequest.getProgress() < 100:
        self.update_state(
            state="PROGRESS",
            meta={
                'currentID': gallicaRequest.getCurrentID(),
                'progress': gallicaRequest.getProgress(),
            })
        time.sleep(1)
    self.update_state(state="SUCCESS")
    return {'progress': 100, 'status': 'Complete!', 'result': 42}
