import sys
import psutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt, QTimer
from enum import Enum, auto

# --- Constantes ---
APP_TITLE = "Apagado Automático por Procesos"
COUNTDOWN_SECONDS = 30
MONITORING_INTERVAL_SECONDS = 10
MAX_INTERVAL_SECONDS = 3600

# --- Colores y Estilos ---
STYLE_BTN_START = "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
STYLE_BTN_CANCEL = "background-color: #f44336; color: white; font-weight: bold; padding: 10px;"

# --- Estados de la UI ---
class UIState(Enum):
    IDLE = auto()
    MONITORING = auto()
    SHUTDOWN_COUNTDOWN = auto()

# --- Worker de Monitoreo ---
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
            self.error.emit("No se seleccionaron procesos.")
            return

        self.progress.emit(f"Monitoreando {len(self.pids_to_watch)} proceso(s)...")
        while self._is_running and self.pids_to_watch:
            self.pids_to_watch = [pid for pid in self.pids_to_watch if psutil.pid_exists(pid)]
            if not self.pids_to_watch:
                self.progress.emit("Todos los procesos finalizaron.")
                self.finished.emit()
                break

            names = [psutil.Process(pid).name() for pid in self.pids_to_watch if psutil.pid_exists(pid)]
            self.progress.emit(f"Esperando a: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")
            
            for _ in range(self.interval):
                if not self._is_running:
                    self.progress.emit("Monitoreo cancelado.")
                    return
                time.sleep(1)

    def stop(self):
        self._is_running = False

# --- Ventana Principal ---
class ProcessShutdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, 600, 500)
        
        self.monitor_thread = None
        self.monitor_worker = None
        self.shutdown_timer = QTimer(self)
        self.countdown = COUNTDOWN_SECONDS

        self._setup_ui()
        self._connect_signals()
        self.populate_process_list() # Poblar la lista al inicio
        self.set_ui_state(UIState.IDLE)

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.process_list_widget = QListWidget()
        self.process_list_widget.setSortingEnabled(True)
        layout.addWidget(QLabel("Procesos para monitorear:"))
        layout.addWidget(self.process_list_widget)

        controls_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refrescar")
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Intervalo (seg):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, MAX_INTERVAL_SECONDS)
        self.interval_spinbox.setValue(MONITORING_INTERVAL_SECONDS)
        controls_layout.addWidget(self.interval_spinbox)
        layout.addLayout(controls_layout)

        self.start_button = QPushButton("Iniciar Monitoreo y Apagar")
        self.start_button.setStyleSheet(STYLE_BTN_START)
        layout.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancelar Apagado")
        self.cancel_button.setStyleSheet(STYLE_BTN_CANCEL)
        layout.addWidget(self.cancel_button)

    def _connect_signals(self):
        self.refresh_button.clicked.connect(self.populate_process_list)
        self.start_button.clicked.connect(self.start_monitoring)
        self.cancel_button.clicked.connect(self.cancel_shutdown)
        self.shutdown_timer.timeout.connect(self.update_shutdown_countdown)

    def set_ui_state(self, state):
        self.start_button.setVisible(state == UIState.IDLE)
        self.cancel_button.setVisible(state == UIState.SHUTDOWN_COUNTDOWN)
        
        is_idle = state == UIState.IDLE
        self.process_list_widget.setEnabled(is_idle)
        self.refresh_button.setEnabled(is_idle)
        self.interval_spinbox.setEnabled(is_idle)
        self.start_button.setEnabled(is_idle)

        if state == UIState.IDLE:
            self.statusBar().showMessage("Listo.")
            self.start_button.setText("Iniciar Monitoreo y Apagar")
        elif state == UIState.MONITORING:
            self.start_button.setText("Monitoreando...")
            self.start_button.setEnabled(False) # Deshabilitado pero visible
            self.start_button.setVisible(True)

    def populate_process_list(self):
        self.process_list_widget.clear()
        try:
            current_user = psutil.Process().username()
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                if proc.info.get('username') == current_user and proc.info.get('name'):
                    item = QListWidgetItem(f"{proc.info['name']} (PID: {proc.info['pid']})")
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    item.setData(Qt.ItemDataRole.UserRole, proc.info['pid'])
                    self.process_list_widget.addItem(item)
        except (psutil.Error) as e:
            self.statusBar().showMessage(f"Error al leer procesos: {e}")

    def start_monitoring(self):
        pids = [self.process_list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.process_list_widget.count()) 
                if self.process_list_widget.item(i).checkState() == Qt.CheckState.Checked]

        if not pids:
            QMessageBox.warning(self, "Selección Vacía", "Seleccione al menos un proceso.")
            return

        self.set_ui_state(UIState.MONITORING)
        
        self.monitor_thread = QThread()
        self.monitor_worker = MonitorWorker(pids, self.interval_spinbox.value())
        self.monitor_worker.moveToThread(self.monitor_thread)
        
        self.monitor_worker.finished.connect(self.start_shutdown_countdown)
        self.monitor_worker.progress.connect(self.statusBar().showMessage)
        self.monitor_worker.error.connect(self.on_monitoring_error)
        self.monitor_thread.started.connect(self.monitor_worker.run)
        self.monitor_thread.finished.connect(self.monitor_thread.deleteLater)
        
        self.monitor_thread.start()

    def on_monitoring_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.set_ui_state(UIState.IDLE)

    def start_shutdown_countdown(self):
        self.set_ui_state(UIState.SHUTDOWN_COUNTDOWN)
        self.countdown = COUNTDOWN_SECONDS
        self.update_shutdown_countdown()
        self.shutdown_timer.start(1000)

    def update_shutdown_countdown(self):
        if self.countdown > 0:
            self.statusBar().showMessage(f"Apagando en {self.countdown}s... Clic en 'Cancelar' para detener.")
            self.countdown -= 1
        else:
            self.shutdown_timer.stop()
            self.initiate_shutdown()

    def cancel_shutdown(self):
        self.shutdown_timer.stop()
        self.set_ui_state(UIState.IDLE)
        self.statusBar().showMessage("Apagado cancelado.")

    def initiate_shutdown(self):
        self.statusBar().showMessage("Apagando el sistema...")
        try:
            if sys.platform in ["linux", "darwin"]:
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            else:
                self.on_monitoring_error(f"Apagado no soportado en {sys.platform}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            msg = f"No se pudo apagar: {e}. Puede requerir privilegios de administrador."
            QMessageBox.critical(self, "Error de Apagado", msg)
            self.set_ui_state(UIState.IDLE)

    def closeEvent(self, event):
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_worker.stop()
            self.monitor_thread.quit()
            self.monitor_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProcessShutdownApp()
    window.show()
    sys.exit(app.exec())