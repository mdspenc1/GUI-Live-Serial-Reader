import threading

class smart_thread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(smart_thread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()
    
    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()
    
    def restart(self):
        self._stop_event.clear()