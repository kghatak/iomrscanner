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
        
        # Open PDF action
        open_pdf_action = QAction('Open PDF', self)
        open_pdf_action.setStatusTip('Open a PDF and extract images from pages')
        open_pdf_action.triggered.connect(self.open_pdf_and_extract_images)
        file_menu.addAction(open_pdf_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        # Button to create QR code to connect to http server from mobile
        qr_code_action = QAction('Create QR Code', self)
        qr_code_action.setStatusTip('Create a QR code to connect to the HTTP server from your mobile device')
        qr_code_action.triggered.connect(self.image_panel.create_qr_code)
        view_menu.addAction(qr_code_action)
        
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

    def qr_code_action(self):
        """Create a QR code for the HTTP server connection"""
        self.image_panel.create_qr_code()
        self.statusBar().showMessage('QR Code created for HTTP server connection')
         
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
        
    def open_pdf_and_extract_images(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        try:
            from pdf2image import convert_from_path
        except ImportError:
            QMessageBox.critical(self, "Missing Dependency", "Please install pdf2image and poppler-utils (brew install poppler)")
            return
        import os
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not pdf_path:
            return
        output_folder = os.path.splitext(pdf_path)[0] + "_pages"
        os.makedirs(output_folder, exist_ok=True)
        try:
            images = convert_from_path(pdf_path)
            image_paths = []
            for i, img in enumerate(images):
                img_path = os.path.join(output_folder, f"page_{i+1}.png")
                img.save(img_path, "PNG")
                image_paths.append(img_path)
            QMessageBox.information(self, "PDF Extracted", f"Extracted {len(image_paths)} images to {output_folder}")
            # Load these images into the side panel and image panel
            self.results_panel.analyze_folder(output_folder)
            if hasattr(self, 'image_panel'):
                self.image_panel.load_folder(output_folder)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to extract images: {e}")

    def resizeEvent(self, event):
        """Handle window resize to maintain image panel proportions"""
        super().resizeEvent(event)
        if hasattr(self, 'splitter'):
            # Calculate new sizes maintaining 20% for image panel (max 300px)
            total_width = self.splitter.width()
            image_panel_width = min(300, int(total_width * 0.2))
            results_panel_width = total_width - image_panel_width
            self.splitter.setSizes([image_panel_width, results_panel_width])
            
    def add_log_message(self, message):
        """Append a log message to the bottom of the results panel log area."""
        try:
            
            print("[DEBUG UI LOG] Slot entered")
            print(f"[DEBUG UI LOG] Message type: {type(message)}, value: {message}")

            if hasattr(self, 'results_panel') and hasattr(self.results_panel, 'add_to_processing_log'):
                print("[DEBUG UI LOG] Calling results_panel.add_to_processing_log")
                self.results_panel.add_to_processing_log(message)
                print("[DEBUG UI LOG] Called results_panel.add_to_processing_log successfully")
            else:
                print("[DEBUG UI LOG] results_panel or add_to_processing_log not found")
                print(f"[UI LOG] {message}")

            print("[DEBUG UI LOG] Slot completed")
        except Exception as e:
            print(f"[UI LOG ERROR] Exception in add_log_message: {e}")
