from dataclasses import dataclass

@dataclass
class AverageResponseTime:
    average_response_time: float = 0

    def update(self, time):
        if self.average_response_time:
            self.average_response_time = (self.averageResponseTime + time) / 2
        else:
            self.average_response_time = time
        return self.average_response_time

