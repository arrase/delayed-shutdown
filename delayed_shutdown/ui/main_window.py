import sys
import subprocess
import psutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QThread, QTimer, Qt
from ..constants import (
    APP_TITLE, MONITORING_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS,
    STYLE_BTN_START, STYLE_BTN_CANCEL
)
from .styles import get_stylesheet
from .ui_state import UIState
from ..core.worker import MonitorWorker

class ProcessShutdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, 600, 500)

        # Initialize components
        self.monitor_thread = None
        self.monitor_worker = None
        self.shutdown_timer = QTimer(self)
        self.countdown = 30
        self.selected_pids = set()  # Use set for more efficient operations

        # Initial configuration
        self._setup_ui()
        self._connect_signals()
        self.populate_process_list()
        self.set_ui_state(UIState.IDLE)
        
        # Apply styles
        self.setStyleSheet(get_stylesheet())

    def _setup_ui(self):
        """Configures the user interface with improved design."""
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
        
        self.cancel_button = QPushButton("Cancel Shutdown")
        self.cancel_button.setStyleSheet(STYLE_BTN_CANCEL)
        layout.addWidget(self.cancel_button)

    def _connect_signals(self):
        """Conecta las señales a sus respectivos slots."""
        self.refresh_button.clicked.connect(self.populate_process_list)
        self.start_button.clicked.connect(self.start_monitoring)
        self.cancel_button.clicked.connect(self.cancel_shutdown)
        self.shutdown_timer.timeout.connect(self.update_shutdown_countdown)
        self.process_list_widget.itemChanged.connect(self._update_selected_pids)

    def _update_selected_pids(self, item):
        """Actualiza el conjunto de PIDs seleccionados cuando cambia el estado de un item."""
        pid = item.data(Qt.ItemDataRole.UserRole)
        if item.checkState() == Qt.CheckState.Checked:
            self.selected_pids.add(pid)
        else:
            self.selected_pids.discard(pid)

    def set_ui_state(self, state):
        """Actualiza la interfaz según el estado actual."""
        is_idle = state == UIState.IDLE
        
        # Main button visibility
        self.start_button.setVisible(is_idle or state == UIState.MONITORING)
        self.cancel_button.setVisible(state == UIState.SHUTDOWN_COUNTDOWN)
        
        # Control enablement
        self.process_list_widget.setEnabled(is_idle)
        self.refresh_button.setEnabled(is_idle)
        self.interval_spinbox.setEnabled(is_idle)
        self.shutdown_spinbox.setEnabled(is_idle)
        
        # Start button state
        if state == UIState.IDLE:
            self.start_button.setText("Start Monitoring and Shutdown")
            self.start_button.setEnabled(True)
            self.statusBar().showMessage("Ready.")
        elif state == UIState.MONITORING:
            self.start_button.setText("Monitoring...")
            self.start_button.setEnabled(False)

    def toggle_item_check(self, item):
        """Invierte el estado de selección de un elemento en la lista."""
        new_state = Qt.CheckState.Unchecked if item.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked
        item.setCheckState(new_state)

    def populate_process_list(self):
        """Rellena la lista de procesos de forma más eficiente."""
        current_selection = self.selected_pids.copy()
        self.process_list_widget.clear()
        self.selected_pids.clear()
        
        try:
            current_user = psutil.Process().username()
            # Get processes in a single call
            processes = list(psutil.process_iter(['pid', 'name', 'username']))
            
            # Filter and add to list
            for proc in processes:
                proc_info = proc.info
                if proc_info['username'] == current_user and proc_info['name']:
                    item = QListWidgetItem(f"{proc_info['name']} (PID: {proc_info['pid']})")
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    
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
        """Inicia el monitoreo de procesos seleccionados."""
        if not self.selected_pids:
            QMessageBox.warning(self, "Empty Selection", "Select at least one process.")
            return
        
        self.set_ui_state(UIState.MONITORING)
        
        # Create and configure monitoring thread
        self.monitor_thread = QThread()
        self.monitor_worker = MonitorWorker(self.selected_pids, self.interval_spinbox.value())
        self.monitor_worker.moveToThread(self.monitor_thread)
        
        # Connect signals
        self.monitor_worker.finished.connect(self.start_shutdown_countdown)
        self.monitor_worker.progress.connect(self.statusBar().showMessage)
        self.monitor_worker.error.connect(self.on_monitoring_error)
        self.monitor_thread.started.connect(self.monitor_worker.run)
        self.monitor_thread.finished.connect(self.monitor_thread.deleteLater)
        
        self.monitor_thread.start()

    def on_monitoring_error(self, message):
        """Maneja errores durante el monitoreo."""
        QMessageBox.critical(self, "Error", message)
        self.set_ui_state(UIState.IDLE)

    def start_shutdown_countdown(self):
        """Inicia la cuenta atrás para el apagado."""
        self.set_ui_state(UIState.SHUTDOWN_COUNTDOWN)
        self.countdown = self.shutdown_spinbox.value()
        self.update_shutdown_countdown()
        self.shutdown_timer.start(1000)

    def update_shutdown_countdown(self):
        """Actualiza la cuenta atrás y muestra el tiempo restante."""
        if self.countdown > 0:
            self.statusBar().showMessage(f"Shutting down in {self.countdown}s... Click 'Cancel' to stop.")
            self.countdown -= 1
        else:
            self.shutdown_timer.stop()
            self.initiate_shutdown()

    def cancel_shutdown(self):
        """Cancela el apagado programado."""
        self.shutdown_timer.stop()
        self.set_ui_state(UIState.IDLE)
        self.statusBar().showMessage("Shutdown canceled.")

    def initiate_shutdown(self):
        """Inicia el proceso de apagado del sistema."""
        self.statusBar().showMessage("Shutting down the system...")
        try:
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            msg = f"Could not shut down: {e}. It may require administrator privileges."
            QMessageBox.critical(self, "Shutdown Error", msg)
            self.set_ui_state(UIState.IDLE)

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_worker.stop()
            self.monitor_thread.quit()
            self.monitor_thread.wait()
        event.accept()
