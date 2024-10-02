from threading import Thread
from time import sleep


class ExecLater(Thread):
    def __init__(self, microseconds: float, func: callable):
        super(ExecLater, self).__init__()

        self.func = func
        self.microseconds = microseconds

    def run(self):
        sleep(self.microseconds / 1000.0)
        self.func()
