from celery import Celery
from gallica.factories.requestFactory import RequestFactory
import time
from gallica.ticket import Ticket

app = Celery()
app.config_from_object('celery_settings')


@app.task(bind=True)
def spawnRequest(self, tickets, requestid):
    ticketOptions = [
        Ticket(
            key=key,
            terms=ticket['terms'],
            codes=ticket['codes'],
            dateRange=ticket['dateRange'],
        )
        for key, ticket in tickets.items()
    ]
    request = RequestFactory(
        ticketOptions,
        requestid
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
        elif request.noRecords:
            return {
                'status': 'No records found!',
                'numRecords': 0
            }
        else:
            self.update_state(
                state="PROGRESS",
                meta={'progress': request.getProgressStats()})
            time.sleep(1)


class TooManyRecordsFailure(Exception):
    pass

