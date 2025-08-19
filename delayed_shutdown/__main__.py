import sys
from PyQt6.QtWidgets import QApplication
from delayed_shutdown.ui.app import App

def main():
    app = QApplication(sys.argv)
    main_app = App(app)
    sys.exit(main_app.run())

if __name__ == "__main__":
    main()
