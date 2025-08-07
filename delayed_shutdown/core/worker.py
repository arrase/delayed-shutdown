import time
import psutil
from PyQt6.QtCore import QObject, pyqtSignal

class MonitorWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, pids_to_watch, interval):
        super().__init__()
        self.pids_to_watch = set(pids_to_watch)  # Usar set para búsquedas más eficientes
        self.interval = interval
        self._is_running = True
        self._process_names = {}  # Cache para nombres de procesos

    def run(self):
        if not self.pids_to_watch:
            self.error.emit("No processes were selected.")
            return

        self.progress.emit(f"Monitoring {len(self.pids_to_watch)} process(es)...")
        
        while self._is_running and self.pids_to_watch:
            # Update list of existing PIDs more efficiently
            active_pids = {pid for pid in self.pids_to_watch if psutil.pid_exists(pid)}
            
            # Si no quedan procesos activos, terminar
            if not active_pids:
                self.progress.emit("All processes have finished.")
                self.finished.emit()
                break
                
            # Actualizar lista de PIDs a monitorizar
            self.pids_to_watch = active_pids
            
            # Obtener nombres de procesos con cache
            names = []
            for pid in active_pids:
                if pid not in self._process_names:
                    try:
                        self._process_names[pid] = psutil.Process(pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        self._process_names[pid] = f"PID:{pid}"
                names.append(self._process_names[pid])
                
            name_str = ', '.join(names[:3])
            if len(names) > 3:
                name_str += '...'
            self.progress.emit(f"Waiting for: {name_str}")

            # Dormir de forma más responsiva
            for _ in range(self.interval):
                if not self._is_running:
                    self.progress.emit("Monitoring canceled.")
                    return
                time.sleep(1)

    def stop(self):
        self._is_running = False
