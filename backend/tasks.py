from celery import Celery
from factories.requestFactory import RequestFactory
import time
from ticket import Ticket

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets):
    ticketOptions = [
        Ticket(
            key=key,
            terms=ticket['terms'],
            codes=ticket['codes'],
            startYear=ticket['startYear'],
            endYear=ticket['endYear']
        )
        for key, ticket in tickets.items()
    ]
    request = RequestFactory(
        ticketOptions,
        self.request.id
    ).build()
    request.start()
    while True:
        if request.finished:
            return {
                'status': 'Complete!',
                'result': 42}
        elif request.tooManyRecords:
            return {
                'status': 'Too many records!',
                'numRecords': request.estimateNumRecords
            }
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': request.getProgressStats()})
            time.sleep(1)


class TooManyRecordsFailure(Exception):
    pass

