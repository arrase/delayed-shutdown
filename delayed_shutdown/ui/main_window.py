import sys
import subprocess
import psutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, QTimer, Qt
from enum import Enum, auto
from .styles import get_stylesheet
from ..core.worker import MonitorWorker

APP_TITLE = "Automatic Process-based Shutdown"
MONITORING_INTERVAL_SECONDS = 10
MAX_INTERVAL_SECONDS = 3600

class UIState(Enum):
    IDLE = auto()
    MONITORING = auto()
    SHUTDOWN_COUNTDOWN = auto()

class ProcessShutdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, 600, 500)

        self.monitor_thread = None
        self.monitor_worker = None
        self.shutdown_timer = QTimer(self)
        self.countdown = 30

        self._setup_ui()
        self._connect_signals()
        self.populate_process_list() # Populate the list on startup
        self.set_ui_state(UIState.IDLE)

        self.setStyleSheet(get_stylesheet())

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.process_list_widget = QListWidget()
        self.process_list_widget.setSortingEnabled(True)
        layout.addWidget(QLabel("Processes to monitor:"))
        layout.addWidget(self.process_list_widget)

        controls_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Interval (sec):"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, MAX_INTERVAL_SECONDS)
        self.interval_spinbox.setValue(MONITORING_INTERVAL_SECONDS)
        controls_layout.addWidget(self.interval_spinbox)

        controls_layout.addWidget(QLabel("Shutdown in (sec):"))
        self.shutdown_spinbox = QSpinBox()
        self.shutdown_spinbox.setRange(1, MAX_INTERVAL_SECONDS)
        self.shutdown_spinbox.setValue(30)
        controls_layout.addWidget(self.shutdown_spinbox)

        layout.addLayout(controls_layout)

        self.start_button = QPushButton("Start Monitoring and Shutdown")
        self.start_button.setObjectName("start-button")
        layout.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel Shutdown")
        self.cancel_button.setObjectName("cancel-button")
        layout.addWidget(self.cancel_button)

    def _connect_signals(self):
        self.refresh_button.clicked.connect(self.populate_process_list)
        self.start_button.clicked.connect(self.start_monitoring)
        self.cancel_button.clicked.connect(self.cancel_shutdown)
        self.shutdown_timer.timeout.connect(self.update_shutdown_countdown)
        self.process_list_widget.itemClicked.connect(self.toggle_item_check)

    def set_ui_state(self, state):
        self.start_button.setVisible(state == UIState.IDLE)
        self.cancel_button.setVisible(state == UIState.SHUTDOWN_COUNTDOWN)

        is_idle = state == UIState.IDLE
        self.process_list_widget.setEnabled(is_idle)
        self.refresh_button.setEnabled(is_idle)
        self.interval_spinbox.setEnabled(is_idle)
        self.shutdown_spinbox.setEnabled(is_idle)
        self.start_button.setEnabled(is_idle)

        if state == UIState.IDLE:
            self.statusBar().showMessage("Ready.")
            self.start_button.setText("Start Monitoring and Shutdown")
        elif state == UIState.MONITORING:
            self.start_button.setText("Monitoring...")
            self.start_button.setEnabled(False) # Disabled but visible
            self.start_button.setVisible(True)

    def toggle_item_check(self, item):
        item.setCheckState(
            Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        )

    def populate_process_list(self):
        self.process_list_widget.clear()
        try:
            current_user = psutil.Process().username()
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                if proc.info.get('username') == current_user and proc.info.get('name'):
                    item = QListWidgetItem(f"{proc.info['name']} (PID: {proc.info['pid']})")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    item.setData(Qt.ItemDataRole.UserRole, proc.info['pid'])
                    self.process_list_widget.addItem(item)
        except (psutil.Error) as e:
            self.statusBar().showMessage(f"Error reading processes: {e}")

    def start_monitoring(self):
        pids = [self.process_list_widget.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.process_list_widget.count())
                if self.process_list_widget.item(i).checkState() == Qt.CheckState.Checked]

        if not pids:
            QMessageBox.warning(self, "Empty Selection", "Select at least one process.")
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
        self.countdown = self.shutdown_spinbox.value()
        self.update_shutdown_countdown()
        self.shutdown_timer.start(1000)

    def update_shutdown_countdown(self):
        if self.countdown > 0:
            self.statusBar().showMessage(f"Shutting down in {self.countdown}s... Click 'Cancel' to stop.")
            self.countdown -= 1
        else:
            self.shutdown_timer.stop()
            self.initiate_shutdown()

    def cancel_shutdown(self):
        self.shutdown_timer.stop()
        self.set_ui_state(UIState.IDLE)
        self.statusBar().showMessage("Shutdown canceled.")

    def initiate_shutdown(self):
        self.statusBar().showMessage("Shutting down the system...")
        try:
            if sys.platform == "linux":
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            else:
                self.on_monitoring_error(f"Shutdown not supported on {sys.platform}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            msg = f"Could not shut down: {e}. It may require administrator privileges."
            QMessageBox.critical(self, "Shutdown Error", msg)
            self.set_ui_state(UIState.IDLE)

    def closeEvent(self, event):
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_worker.stop()
            self.monitor_thread.quit()
            self.monitor_thread.wait()
        event.accept()
