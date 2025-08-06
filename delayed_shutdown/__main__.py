import sys
from PyQt6.QtWidgets import QApplication
from .main_window import ProcessShutdownApp

def main():
    app = QApplication(sys.argv)
    window = ProcessShutdownApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()