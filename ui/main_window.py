from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QMenuBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from .image_panel import ImagePanel
from .results_panel import ResultsPanel


class MainWindow(QMainWindow):
    folder_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Folder Analyzer")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
        self.init_ui()
        self.create_menu()
        
    def init_ui(self):
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Create panels
        self.image_panel = ImagePanel()
        self.results_panel = ResultsPanel()
        
        # Set image panel constraints
        self.image_panel.setMaximumWidth(300)
        self.image_panel.setMinimumWidth(200)
        
        # Add panels to splitter
        splitter.addWidget(self.image_panel)
        splitter.addWidget(self.results_panel)
        
        # Calculate initial sizes (20% for images, 80% for results, but respect max width)
        window_width = 1200  # Default window width
        image_panel_width = min(300, int(window_width * 0.2))  # 20% but max 300px
        results_panel_width = window_width - image_panel_width
        splitter.setSizes([image_panel_width, results_panel_width])
        
        # Set stretch factors to maintain proportions when resizing
        splitter.setStretchFactor(0, 0)  # Image panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Results panel takes remaining space
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Store splitter reference for resize events
        self.splitter = splitter
        
        # Connect signals
        self.folder_selected.connect(self.image_panel.load_folder)
        self.folder_selected.connect(self.results_panel.analyze_folder)
        self.image_panel.image_selected.connect(self.results_panel.show_image_details)
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Open folder action
        open_folder_action = QAction('&Open Folder', self)
        open_folder_action.setShortcut('Ctrl+O')
        open_folder_action.setStatusTip('Open a folder containing images')
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        # Refresh action
        refresh_action = QAction('&Refresh', self)
        refresh_action.setShortcut('F5')
        refresh_action.setStatusTip('Refresh current folder')
        refresh_action.triggered.connect(self.refresh_current_folder)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        # About action
        about_action = QAction('&About', self)
        about_action.setStatusTip('About this application')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
    def open_folder(self):
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Folder Containing Images",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.statusBar().showMessage(f'Loading folder: {folder}')
            self.folder_selected.emit(folder)
            self.statusBar().showMessage(f'Loaded: {folder}')
            
    def refresh_current_folder(self):
        current_folder = self.image_panel.current_folder
        if current_folder:
            self.folder_selected.emit(current_folder)
            self.statusBar().showMessage('Refreshed')
        else:
            self.statusBar().showMessage('No folder selected')
            
    def show_about(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About Image Folder Analyzer",
            "Image Folder Analyzer v1.0\n\n"
            "A tool for analyzing and viewing images in folders.\n"
            "Built with PyQt5."
        )
        
    def resizeEvent(self, event):
        """Handle window resize to maintain image panel proportions"""
        super().resizeEvent(event)
        if hasattr(self, 'splitter'):
            # Calculate new sizes maintaining 20% for image panel (max 300px)
            total_width = self.splitter.width()
            image_panel_width = min(300, int(total_width * 0.2))
            results_panel_width = total_width - image_panel_width
            self.splitter.setSizes([image_panel_width, results_panel_width])
