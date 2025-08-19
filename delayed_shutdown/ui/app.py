
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon
from .main_window import ProcessShutdownApp

class App:
    def __init__(self, app: QApplication):
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            sys.exit(1)

        self.main_window = ProcessShutdownApp()
        self._setup_system_tray()

    def _setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon()
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "icon.png")
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("Delayed Shutdown")
        self.tray_icon.activated.connect(self._on_tray_activated)
        self._setup_tray_menu()
        self.tray_icon.show()

    def _setup_tray_menu(self):
        menu = QMenu()
        show_action = QAction("Show", self.main_window)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)
        menu.addSeparator()
        exit_action = QAction("Exit", self.main_window)
        exit_action.triggered.connect(self.app.quit)
        menu.addAction(exit_action)
        self.tray_icon.setContextMenu(menu)

    def _show_window(self):
        self.main_window.showNormal()
        self.main_window.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self._show_window()

    def run(self):
        self.main_window.hide()
        return self.app.exec()
