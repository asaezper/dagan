from contextlib import contextmanager

from dagan.utils.rw_lock import RWLock


class DaganRWLock(RWLock):
    @contextmanager
    def reader(self):
        self.reader_acquire()
        yield
        self.reader_release()

    @contextmanager
    def writer(self):
        self.writer_acquire()
        yield
        self.writer_release()
