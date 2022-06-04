from requestThread import RequestThread
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.result_backend = 'redis://localhost:6379/0'


@celery.task(bind=True)
def getAsyncRequest(self, tickets):
    gallicaRequest = RequestThread(tickets)
    gallicaRequest.start()
    while gallicaRequest.getProgress() < 100:
        self.update_state(meta={
            'status': "Fetching...",
            'id': gallicaRequest.getCurrentID(),
            'percent': gallicaRequest.getProgress(),
        })
    self.update_state(
        state="SUCCESS",
        meta={
            'status': "All done.",
            'graphJSON': gallicaRequest.getGraphJSON()
        })
    return {'percent': 100, 'status': 'Complete!', 'result': 42}
