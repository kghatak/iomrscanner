import sys

import threading
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt5.QtCore import QObject, pyqtSignal

# --- Flask server setup ---
from flask import Flask

flask_app = Flask(__name__)

# This will be set to the MainWindow instance after UI is created
main_window_instance = None

@flask_app.route('/connect', methods=['GET'])
def connect():
    print("[Flask] /connect API called from browser!")
    # Log to the UI if possible
    if main_window_instance is not None:
        try:
            # Assumes main_window_instance has a method or attribute to log messages
            print(f"[DEBUG UI LOG] [Flask] Main Window found: Writing log!")
            main_window_instance.add_log_message("[Flask] /connect API called from browser!")
        except Exception as e:
            print(f"[Flask] Could not log to UI: {e}")
    return 'Connected to Bignan Mancha OMR Reader Flask server!'

def run_flask():
    flask_app.run(host='0.0.0.0', port=5023, debug=False, use_reloader=False)

class CrossThreadSignalProcessor(QObject):
    log_message_signal = pyqtSignal(str)
    # You can add more signals here for other cross-thread events

    def __init__(self, parent=None):
        super().__init__(parent)

# Create a global signal processor instance
signal_processor = CrossThreadSignalProcessor()

def main():
    global main_window_instance
    app = QApplication(sys.argv)
    app.setApplicationName("Bignan Mancha OMR Reader")
    app.setApplicationVersion("2.1.0")

    # Apply global style
    app.setStyleSheet("""
        QApplication {
            font-family: 'Arial', sans-serif;
        }
    """)

    # Start Flask server in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    window = MainWindow()
    main_window_instance = window
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
