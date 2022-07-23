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
    while not gallicaRequest.isFinished():
        self.update_state(
            state="PROGRESS",
            meta={
                'progress': gallicaRequest.getKeyedProgress()
            })
    self.update_state(state="SUCCESS")
    return {'progress': 100, 'status': 'Complete!', 'result': 42}
