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
        
        # Set window icon
        self.set_app_icon()
        
        self.init_ui()
        self.create_menu()
    
    def set_app_icon(self):
        """Set the application window icon"""
        try:
            import os
            # Get the icon path (relative to this file)
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'assets', 
                'app_icon.png'
            )
            
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                # Also set for all windows
                from PyQt5.QtWidgets import QApplication
                QApplication.setWindowIcon(icon)
            else:
                print(f"Warning: Icon not found at {icon_path}")
        except Exception as e:
            print(f"Warning: Could not set app icon: {e}")
        
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
        
        # Connect results panel folder loading to image panel
        self.results_panel.folder_loaded.connect(self.image_panel.load_folder)
        
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
        
        # Upload Result action
        upload_result_action = QAction('Upload Result', self)
        upload_result_action.setStatusTip('Upload CSV result file with exam data')
        upload_result_action.triggered.connect(self.upload_result_csv)
        file_menu.addAction(upload_result_action)
        
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
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        # ML Dataset Review action
        review_action = QAction('🔍 Review ML Dataset Labels', self)
        review_action.setStatusTip('Open manual review tool for ML dataset labels')
        review_action.triggered.connect(self.open_review_tool)
        tools_menu.addAction(review_action)
        
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

    def upload_result_csv(self):
        """Upload CSV result file and display in new tab."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import csv
        import os
        
        # Open file dialog for CSV selection
        csv_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select CSV Result File", 
            "", 
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not csv_path:
            return
        
        try:
            # Read CSV file
            results_data = []
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate required columns
                required_columns = ['examname', 'class', 'questionIndex', 'correctchoice', 'questiontype']
                if not all(col in reader.fieldnames for col in required_columns):
                    missing_cols = [col for col in required_columns if col not in reader.fieldnames]
                    QMessageBox.warning(
                        self, 
                        "Invalid CSV Format", 
                        f"Missing required columns: {', '.join(missing_cols)}\n\n"
                        f"Required format: examname, class, questionIndex, correctchoice, questiontype"
                    )
                    return
                
                # Read all rows
                for row in reader:
                    results_data.append(row)
            
            if not results_data:
                QMessageBox.warning(self, "Empty File", "The CSV file contains no data.")
                return
            
            # Add uploaded results to the results panel
            self.results_panel.add_uploaded_results_tab(results_data)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Upload Successful", 
                f"Successfully uploaded {len(results_data)} result records from {os.path.basename(csv_path)}"
            )
            
            # Switch to the uploaded results tab
            self.results_panel.show_uploaded_results_tab()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload CSV file: {str(e)}")

    def open_review_tool(self):
        """Open the ML Dataset Manual Review Tool as a popup window"""
        try:
            # Try to import the review tool
            import sys
            import os
            
            # Add tools directory to path if not already there
            tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            
            # Check if pandas is available
            try:
                import pandas as pd
            except (ImportError, ValueError) as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Missing Dependency",
                    "The ML Dataset Review Tool requires pandas.\n\n"
                    "To fix this issue:\n"
                    "1. Run: ./setup_fresh_env.sh\n"
                    "2. Activate: source venv/bin/activate\n"
                    "3. Restart the application\n\n"
                    f"Error: {str(e)[:100]}"
                )
                return
            
            # Import and create review tool window
            from manual_review_tool import CircleReviewTool
            
            # Create review tool as a separate window (not modal)
            self.review_window = CircleReviewTool()
            self.review_window.show()
            
            self.statusBar().showMessage('Opened ML Dataset Review Tool')
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open review tool:\n{str(e)}\n\n"
                f"Make sure pandas is installed:\n"
                f"./setup_fresh_env.sh"
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
