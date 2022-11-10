class AverageResponseTime:

    def __init__(self):
        self.averageResponseTime = 0

    def get(self):
        return self.averageResponseTime

    def update(self, time):
        if self.averageResponseTime:
            self.averageResponseTime = (self.averageResponseTime + time) / 2
        else:
            self.averageResponseTime = time
        return self.averageResponseTime

