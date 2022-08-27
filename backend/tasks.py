from celery import Celery
from scripts.requestThread import RequestThread

#TODO: rethink celery

celery = Celery(
    'api.tasks',
    broker='redis://redisforcelery.romsqk.ng.0001.usw1.cache.amazonaws.com:6379/0',
    backend='redis://redisforcelery.romsqk.ng.0001.usw1.cache.amazonaws.com:6379/0')


@celery.task(bind=True)
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
