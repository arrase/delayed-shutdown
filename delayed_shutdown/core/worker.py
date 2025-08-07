import time
import psutil
from PyQt6.QtCore import QObject, pyqtSignal

class MonitorWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, pids_to_watch, interval):
        super().__init__()
        self.pids_to_watch = set(pids_to_watch)  # Use set for more efficient searches
        self.interval = interval
        self._is_running = True
        self._process_names = {}  # Cache for process names

    def run(self):
        if not self.pids_to_watch:
            self.error.emit("No processes were selected.")
            return

        self.progress.emit(f"Monitoring {len(self.pids_to_watch)} process(es)...")
        
        while self._is_running and self.pids_to_watch:
            # Update list of existing PIDs more efficiently
            active_pids = {pid for pid in self.pids_to_watch if psutil.pid_exists(pid)}
            
            # If no active processes remain, terminate
            if not active_pids:
                self.progress.emit("All processes have finished.")
                self.finished.emit()
                break
                
            # Update list of PIDs to monitor
            self.pids_to_watch = active_pids

            # Cleanup process name cache for PIDs no longer monitored
            self._process_names = {pid: name for pid, name in self._process_names.items() if pid in active_pids}
            
            # Get process names with cache
            names = []
            for pid in active_pids:
                if pid not in self._process_names:
                    try:
                        self._process_names[pid] = psutil.Process(pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        self._process_names[pid] = f"Unknown (PID: {pid})"
                names.append(self._process_names[pid])
                
            name_str = ', '.join(names[:3])
            if len(names) > 3:
                name_str += '...'
            self.progress.emit(f"Waiting for: {name_str}")

            # Sleep more responsively
            for _ in range(self.interval):
                if not self._is_running:
                    self.progress.emit("Monitoring canceled.")
                    return
                time.sleep(1)

    def stop(self):
        self._is_running = False
