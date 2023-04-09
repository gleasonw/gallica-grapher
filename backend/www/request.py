import threading
import io
from www.models import Ticket, Progress
from www.database.connContext import build_db_conn
from typing import Callable, Literal
import www.pyllicaWrapper as pyllica_wrapper


class Request:
    """A co-routine that spawns for each user and calls the core fetch --> parse --> store to database logic"""

    def __init__(
        self,
        ticket: Ticket,
        id: int,
        on_update_progress: Callable[[Progress], None],
    ):
        self.id = id
        self.on_update_progress = on_update_progress
        self.ticket = ticket
        self.num_records = 0
        self.num_requests_sent = 0
        self.total_requests = 0
        self.average_response_time = 0
        self.random_paper_for_progress = ""
        self.estimate_seconds_to_completion = 0
        self.state: Literal[
            "too_many_records", "completed", "error", "no_records", "running"
        ] = "running"
        super().__init__()

    async def run(self):
        """Fetch records for user from Pyllica and insert to DB for graphing"""
        with build_db_conn() as db_conn:
            if pyllica_records := await pyllica_wrapper.get(
                self.ticket, on_no_records_found=self.set_no_records
            ):

                def clean_csv_row(value):
                    if value is None:
                        return r"\N"
                    return str(value).replace("|", "\\|")

                csv_file_like_object = io.StringIO()
                for record in pyllica_records:
                    row = (
                        record.year,
                        record.month,
                        record.day,
                        record.term,
                        self.id,
                        record.count,
                    )
                    csv_file_like_object.write("|".join(map(clean_csv_row, row)) + "\n")

                csv_file_like_object.seek(0)
                with db_conn.cursor() as curs:
                    curs.copy_from(
                        csv_file_like_object,
                        "groupcounts",
                        sep="|",
                        columns=(
                            "year",
                            "month",
                            "day",
                            "searchterm",
                            "requestid",
                            "count",
                        ),
                    )
            if self.state not in ["too_many_records", "no_records"]:
                self.state = "completed"
            self.on_update_progress(
                Progress(
                    num_results_discovered=self.num_records,
                    num_requests_to_send=self.total_requests,
                    num_requests_sent=self.num_requests_sent,
                    backend_source=self.ticket.backend_source,
                    estimate_seconds_to_completion=self.estimate_seconds_to_completion,
                    random_paper=self.random_paper_for_progress,
                    state=self.state,
                    random_text="",
                )
            )

    def set_no_records(self):
        self.state = "no_records"
