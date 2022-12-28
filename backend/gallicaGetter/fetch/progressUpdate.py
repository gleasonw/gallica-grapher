from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProgressUpdate:
    elapsed_time: float
    num_workers: int
    xml: bytes
