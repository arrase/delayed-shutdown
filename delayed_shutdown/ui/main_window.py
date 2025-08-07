import sys
import subprocess
import psutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, QTimer, Qt
from .styles import get_stylesheet
from .ui_state import UIState
from ..core.worker import MonitorWorker

# --- Constantes locales ---
APP_TITLE = "Automatic Process-based Shutdown"
MONITORING_INTERVAL_SECONDS = 10
MAX_INTERVAL_SECONDS = 3600
DEFAULT_COUNTDOWN_SECONDS = 30
STYLE_BTN_START = "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
STYLE_BTN_STOP = "background-color: orange; color: white; font-weight: bold; padding: 10px;"
STYLE_BTN_CANCEL = "background-color: #f44336; color: white; font-weight: bold; padding: 10px;"
STYLE_BTN_SHUTDOWN = "background-color: red; color: white; font-weight: bold; padding: 10px;"

class ProcessShutdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, 600, 500)

        # Initialize components
        self.monitor_thread = None
        self.monitor_worker = None
        self.shutdown_timer = QTimer(self)
        self.countdown = DEFAULT_COUNTDOWN_SECONDS
        self.selected_pids = set()  # Use set for more efficient operations

        # Monitoring and countdown state
        self.monitoring_active = False
        self.shutdown_countdown_active = False

        # Initial configuration
        self._setup_ui()
        self._connect_signals()
        self.populate_process_list()
        self.set_ui_state(UIState.IDLE)
        
        # Apply styles
        self.setStyleSheet(get_stylesheet())

    def _setup_ui(self):
        """Configures the user interface."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Process list
        self.process_list_widget = QListWidget()
        self.process_list_widget.setSortingEnabled(True)
        layout.addWidget(QLabel("Processes to monitor:"))
        layout.addWidget(self.process_list_widget)
        
        # Control panel
        controls_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch()
        
        # Interval configuration
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
        
        # Main buttons
        self.start_button = QPushButton("Start Monitoring and Shutdown")
        self.start_button.setStyleSheet(STYLE_BTN_START)
        layout.addWidget(self.start_button)

    def _connect_signals(self):
        """Connects signals to their respective slots."""
        self.refresh_button.clicked.connect(self.populate_process_list)
        self.start_button.clicked.connect(self.handle_main_button)
        self.shutdown_timer.timeout.connect(self.update_shutdown_countdown)
        self.process_list_widget.itemChanged.connect(self._update_selected_pids)
        self.process_list_widget.itemClicked.connect(self.toggle_item_check)

    def _update_selected_pids(self, item):
        """Updates the set of selected PIDs when an item's state changes."""
        pid = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.selected_pids.add(pid)
        else:
            self.selected_pids.discard(pid)

    def set_ui_state(self, state):
        """Updates the interface according to the current state."""
        is_idle = state == UIState.IDLE
        is_monitoring = state == UIState.MONITORING
        is_shutdown = state == UIState.SHUTDOWN_COUNTDOWN

        self.process_list_widget.setEnabled(is_idle)
        self.refresh_button.setEnabled(is_idle)
        self.interval_spinbox.setEnabled(is_idle)
        self.shutdown_spinbox.setEnabled(is_idle)

        if is_idle:
            self.start_button.setText("Start Monitoring and Shutdown")
            self.start_button.setStyleSheet(STYLE_BTN_START)
            self.start_button.setEnabled(True)
            self.monitoring_active = False
            self.shutdown_countdown_active = False
            self.statusBar().showMessage("Ready.")
        elif is_monitoring:
            self.start_button.setText("Stop monitoring")
            self.start_button.setStyleSheet(STYLE_BTN_STOP)
            self.start_button.setEnabled(True)
            self.monitoring_active = True
            self.shutdown_countdown_active = False
            self.statusBar().showMessage("Monitoring processes...")
        elif is_shutdown:
            self.start_button.setText("Cancel shutdown")
            self.start_button.setStyleSheet(STYLE_BTN_SHUTDOWN)
            self.start_button.setEnabled(True)
            self.monitoring_active = False
            self.shutdown_countdown_active = True

    def handle_main_button(self):
        """Handles the main button behavior according to the current state."""
        if self.monitoring_active:
            # Stop monitoring
            self.stop_monitoring()
        elif self.shutdown_countdown_active:
            # Cancel shutdown
            self.cancel_shutdown()
        else:
            # Start monitoring
            self.start_monitoring()

    def toggle_item_check(self, item):
        """Inverts the selection state of a list item."""
        new_state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        item.setCheckState(new_state)

    def populate_process_list(self):
        """Populates the process list."""
        current_selection = self.selected_pids.copy()
        self.process_list_widget.clear()
        self.selected_pids.clear()
        
        try:
            current_user = psutil.Process().username()
            # Get processes in a single call
            # Filter and add to list
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                proc_info = proc.info
                if proc_info['username'] == current_user and proc_info['name']:
                    item = QListWidgetItem(f"{proc_info['name']} (PID: {proc_info['pid']})")
                    # Remove ItemIsUserCheckable to prevent user interaction with checkboxes
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    
                    # Restore previous selection
                    if proc_info['pid'] in current_selection:
                        item.setCheckState(Qt.CheckState.Checked)
                        self.selected_pids.add(proc_info['pid'])
                    else:
                        item.setCheckState(Qt.CheckState.Unchecked)
                        
                    item.setData(Qt.ItemDataRole.UserRole, proc_info['pid'])
                    self.process_list_widget.addItem(item)
                    
        except (psutil.Error) as e:
            self.statusBar().showMessage(f"Error reading processes: {e}")

    def start_monitoring(self):
        """Starts monitoring of selected processes."""
        if not self.selected_pids:
            QMessageBox.warning(self, "Empty Selection", "Select at least one process.")
            return

        self.set_ui_state(UIState.MONITORING)

        self.monitor_thread = QThread()
        self.monitor_worker = MonitorWorker(self.selected_pids.copy(), self.interval_spinbox.value())
        self.monitor_worker.moveToThread(self.monitor_thread)

        self.monitor_worker.finished.connect(self.start_shutdown_countdown)
        self.monitor_worker.progress.connect(self.statusBar().showMessage)
        self.monitor_worker.error.connect(self.on_monitoring_error)
        self.monitor_thread.started.connect(self.monitor_worker.run)
        self.monitor_thread.finished.connect(self.monitor_thread.deleteLater)

        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stops monitoring and returns to the initial state."""
        if self.monitor_worker:
            self.monitor_worker.stop()
        if self.monitor_thread:
            self.monitor_thread.quit()
            self.monitor_thread.wait()
        self.set_ui_state(UIState.IDLE)
        self.statusBar().showMessage("Monitoring canceled.")

    def start_shutdown_countdown(self):
        """Starts the countdown for shutdown."""
        self.set_ui_state(UIState.SHUTDOWN_COUNTDOWN)
        self.countdown = self.shutdown_spinbox.value()
        self.update_shutdown_countdown()
        self.shutdown_timer.start(1000)

    def update_shutdown_countdown(self):
        """Updates the countdown and shows the remaining time."""
        if self.countdown > 0:
            self.statusBar().showMessage(f"Shutting down in {self.countdown}s... Click 'Cancel shutdown' to stop.")
            self.countdown -= 1
        else:
            self.shutdown_timer.stop()
            self.initiate_shutdown()

    def cancel_shutdown(self):
        """Cancels the scheduled shutdown and returns to the initial state."""
        self.shutdown_timer.stop()
        self.set_ui_state(UIState.IDLE)
        self.statusBar().showMessage("Shutdown canceled.")

    def initiate_shutdown(self):
        """Initiates the system shutdown process."""
        self.statusBar().showMessage("Shutting down the system...")
        try:
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            msg = f"Could not shut down: {e}. It may require administrator privileges."
            QMessageBox.critical(self, "Shutdown Error", msg)
            self.set_ui_state(UIState.IDLE)

    def on_monitoring_error(self, message):
        """Handles errors during monitoring."""
        QMessageBox.critical(self, "Error", message)
        self.set_ui_state(UIState.IDLE)

    def closeEvent(self, event):
        """Handles the window close event."""
        # Avoid RuntimeError if QThread has been deleted
        if isinstance(self.monitor_thread, QThread) and self.monitor_thread is not None:
            try:
                if self.monitor_thread.isRunning():
                    self.monitor_worker.stop()
                    self.monitor_thread.quit()
                    self.monitor_thread.wait()
            except RuntimeError:
                pass  # Thread already deleted
        event.accept()
