from pickle import Pickler, load

try:
    from pickle import PickleBuffer
except ImportError:
    PickleBuffer = None
import copyreg
import os
import numpy as np
import time
import gc
import io
from multiprocessing import get_context


def monitor_worker(pid, queue, stop_event, delay=0.05):
    from psutil import Process
    p = Process(pid)
    peak = 0

    def make_measurement(peak):
        mem = p.memory_info().rss
        if mem > peak:
            peak = mem
        return peak

    # Make measurements every 'delay' seconds until we receive the stop event:
    while not stop_event.wait(timeout=delay):
        peak = make_measurement(peak)

    # Make one last measurement in case memory has increased just before
    # receiving the stop event:
    peak = make_measurement(peak)
    queue.put(peak)


class PeakMemoryMonitor:

    _mp = get_context('spawn')

    def __enter__(self):
        pid = os.getpid()
        self.queue = q = self._mp.Queue()
        self.stop_event = e = self._mp.Event()
        self.worker = self._mp.Process(target=monitor_worker, args=(pid, q, e))
        self.worker.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.stop_event.set()
        if exc_type is not None:
            self.worker.terminate()
            return False
        else:
            self.peak = self.queue.get()
            print("peak memory usage: {:.6f} GB".format(self.peak / 1e9))
            return True


def _array_from_buffer(buffer, dtype, shape):
    return np.frombuffer(buffer, dtype=dtype).reshape(shape)


def reduce_ndarray_pickle5(a):
    # This reducer assumes protocol 5 as currently there is no way to register
    # protocol-aware reduce function in the global copyreg dispatch table.
    if not a.dtype.hasobject and a.flags.c_contiguous:
        # No-copy pickling for C-contiguous arrays and protocol 5
        return _array_from_buffer, (PickleBuffer(a), a.dtype, a.shape), None
    else:
        # Fall-back to generic method
        return a.__reduce__()


if __name__ == "__main__":
    print("# Part 1: in-memory dump speed\n")
    # See: https://github.com/numpy/numpy/issues/7544

    for protocol in (4, 5):
        if PickleBuffer is None and protocol == 5:
            continue
        data = np.random.randint(0, 255, dtype='u1', size=1000000000)
        t0 = time.time()
        p = Pickler(io.BytesIO(), protocol=protocol)
        if protocol >= 5:
            p.dispatch_table = copyreg.dispatch_table.copy()
            p.dispatch_table[np.ndarray] = reduce_ndarray_pickle5
        p.dump(data)
        print(f"protocol {protocol} in-memory dump of 1GB in"
              f" {time.time() - t0:0.10}s")
        del p
        del data
        gc.collect()

    print("\n# Part 2: dumping and loading to / from files\n")

    for protocol in (4, 5):
        if PickleBuffer is None and protocol == 5:
            continue

        filename = f'blob_protocol_{protocol}.bin'

        print('Allocating original array...')
        with PeakMemoryMonitor():
            data = np.ones(int(1e9 / 8))

        print(f'Dumping array to {filename}...')
        with PeakMemoryMonitor():
            t0 = time.time()
            with open(filename, 'wb') as f:
                p = Pickler(f, protocol=protocol)
                if protocol >= 5:
                    p.dispatch_table = copyreg.dispatch_table.copy()
                    p.dispatch_table[np.ndarray] = reduce_ndarray_pickle5
                p.dump(data)
                del p
            print(f'done in {time.time() - t0:0.10}s')

        del data
        gc.collect()

        print(f'Loading array back from {filename}...')
        with PeakMemoryMonitor():
            t0 = time.time()
            with open(filename, 'rb') as f:
                data = load(f)
            print(f'done in {time.time() - t0:0.10}s')

        del data
        gc.collect()
