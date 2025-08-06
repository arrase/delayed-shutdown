import time
import psutil
from PyQt6.QtCore import QObject, pyqtSignal

class MonitorWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, pids_to_watch, interval):
        super().__init__()
        self.pids_to_watch = pids_to_watch
        self.interval = interval
        self._is_running = True

    def run(self):
        if not self.pids_to_watch:
            self.error.emit("No processes were selected.")
            return

        self.progress.emit(f"Monitoring {len(self.pids_to_watch)} process(es)...")
        while self._is_running and self.pids_to_watch:
            self.pids_to_watch = [pid for pid in self.pids_to_watch if psutil.pid_exists(pid)]
            if not self.pids_to_watch:
                self.progress.emit("All processes have finished.")
                self.finished.emit()
                break

            names = [psutil.Process(pid).name() for pid in self.pids_to_watch]
            self.progress.emit(f"Waiting for: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")

            for _ in range(self.interval):
                if not self._is_running:
                    self.progress.emit("Monitoring canceled.")
                    return
                time.sleep(1)

    def stop(self):
        self._is_running = False
