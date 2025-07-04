import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Image Folder Analyzer")
    app.setApplicationVersion("1.0")
    
    # Apply global style
    app.setStyleSheet("""
        QApplication {
            font-family: 'Arial', sans-serif;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
