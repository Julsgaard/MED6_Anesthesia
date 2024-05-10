
import time

class TimerClass:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed_time(self):
        if self.start_time is None:
            return 0
        return time.time() - self.start_time

    def reset(self):
        self.start_time = time.time()
