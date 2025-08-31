import os
import json
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QScrollArea, QFrame, QMenu, QAction, QDialog,
    QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox,
    QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon


class ImageLoadThread(QThread):
    image_loaded = pyqtSignal(str, QPixmap)
    
    def __init__(self, image_paths):
        super().__init__()
        self.image_paths = image_paths
        
    def run(self):
        for path in self.image_paths:
            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Scale to smaller thumbnail size for narrow panel
                    thumbnail = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_loaded.emit(path, thumbnail)
            except Exception as e:
                print(f"Error loading image {path}: {e}")


class ImagePanel(QWidget):
    image_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_folder = None
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #e8e8e8;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("📁 Images")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setFont(QFont("Arial", 10))
        self.folder_label.setAlignment(Qt.AlignCenter)
        self.folder_label.setStyleSheet("color: #666; margin-bottom: 5px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.folder_label)
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                text-align: center;
            }
            QListWidget::item:selected {
                background-color: #3f72af;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        # Set icon size for thumbnails (smaller for narrow panel)
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.itemClicked.connect(self.on_image_selected)
        
        # Enable context menu
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_images)
        self.refresh_button.setEnabled(False)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        # Add widgets to main layout
        layout.addWidget(header_frame)
        layout.addWidget(self.image_list)
        layout.addLayout(button_layout)
        
    @pyqtSlot(str)
    def load_folder(self, folder_path):
        self.current_folder = folder_path
        self.folder_label.setText(f"📂 {os.path.basename(folder_path)}")
        self.refresh_button.setEnabled(True)
        self.load_images()
        
    def load_images(self):
        if not self.current_folder:
            return
            
        # Clear existing items
        self.image_list.clear()
        
        # Get image files
        try:
            files = os.listdir(self.current_folder)
            image_files = [
                f for f in files 
                if os.path.splitext(f.lower())[1] in self.image_extensions
            ]
            image_files.sort()
            
            if not image_files:
                item = QListWidgetItem("No images found in this folder")
                item.setFlags(Qt.NoItemFlags)
                self.image_list.addItem(item)
                return
                
            # Get full paths
            image_paths = [os.path.join(self.current_folder, f) for f in image_files]
            
            # Add placeholder items first
            for i, path in enumerate(image_paths):
                filename = os.path.basename(path)
                item = QListWidgetItem(f"Loading... {filename}")
                item.setData(Qt.UserRole, path)
                self.image_list.addItem(item)
            
            # Load thumbnails in background thread
            self.load_thread = ImageLoadThread(image_paths)
            self.load_thread.image_loaded.connect(self.on_thumbnail_loaded)
            self.load_thread.start()
            
        except Exception as e:
            item = QListWidgetItem(f"Error loading folder: {str(e)}")
            item.setFlags(Qt.NoItemFlags)
            self.image_list.addItem(item)
            
    @pyqtSlot(str, QPixmap)
    def on_thumbnail_loaded(self, path, thumbnail):
        # Find the item with this path and update it
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if item.data(Qt.UserRole) == path:
                filename = os.path.basename(path)
                # Get file size
                try:
                    size = os.path.getsize(path)
                    size_str = self.format_file_size(size)
                    item.setText(f"{filename}\n{size_str}")
                except:
                    item.setText(filename)
                
                # Set thumbnail
                item.setIcon(QIcon(thumbnail))
                break
                
    def format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
            
    def on_image_selected(self, item):
        path = item.data(Qt.UserRole)
        if path:
            self.image_selected.emit(path)
            
    def refresh_images(self):
        if self.current_folder:
            self.load_images()

    def create_qr_code(self):
        try:
            import qrcode
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            from PyQt5.QtGui import QPixmap, QImage
            import socket
        except ImportError:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Missing Dependency", "Please install qrcode: pip install qrcode[pil]")
            return

        # Get local IP address
        def get_local_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(0)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception:
                return "127.0.0.1"

        ip = get_local_ip()
        port = 5023  # Change if your server uses a different port
        url = f"http://{ip}:{port}/connect"

        # Generate QR code
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert PIL image to QPixmap
        img = img.convert("RGB")
        data = img.tobytes("raw", "RGB")
        qimg = QImage(data, img.size[0], img.size[1], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        # Show dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("QR Code for HTTP Server Connect")
        layout = QVBoxLayout(dialog)
        label = QLabel(f"Scan this QR code to connect:\n{url}")
        label.setWordWrap(True)
        layout.addWidget(label)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_context_menu(self, position):
        """Show context menu for right-click on image items."""
        item = self.image_list.itemAt(position)
        if not item or not item.data(Qt.UserRole):
            return
        
        image_path = item.data(Qt.UserRole)
        if not image_path:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # Add stage testing submenu
        stage_menu = menu.addMenu("🧪 Test Pipeline Stages")
        
        # Define stages with their descriptions
        stages = [
            ("aruco_check", "🎯 ArUco Marker Detection", "Check if ArUco markers are present"),
            ("orientation_check", "🔄 Orientation Check", "Check and rotate tilted images"),
            ("roll_number_extraction", "📝 Roll Number Extraction", "Extract exam roll number using OCR"),
            ("omr_processing", "📊 OMR Processing", "Process the OMR sheet and extract answers"),
            ("api_upload", "📤 API Upload", "Upload processed data to API")
        ]
        
        # Add stage actions
        for stage_name, stage_title, stage_desc in stages:
            action = QAction(stage_title, self)
            action.setToolTip(stage_desc)
            action.triggered.connect(lambda checked, path=image_path, stage=stage_name: self.test_stage(path, stage))
            stage_menu.addAction(action)
        
        # Add separator
        menu.addSeparator()
        
        # Add "Test All Stages" action
        test_all_action = QAction("🚀 Test All Stages", self)
        test_all_action.setToolTip("Test all pipeline stages in sequence")
        test_all_action.triggered.connect(lambda checked, path=image_path: self.test_all_stages(path))
        menu.addAction(test_all_action)
        
        # Show menu
        menu.exec_(self.image_list.mapToGlobal(position))
    
    def test_stage(self, image_path, stage_name):
        """Test a single pipeline stage on the given image."""
        try:
            # Import stage tester
            from tests.test_single_stage import SingleStageTester
            
            # Create tester
            tester = SingleStageTester()
            
            # Check if stage needs context
            context_needed = self.get_stage_context_requirements(stage_name)
            mock_context = None
            
            if context_needed:
                # Show context input dialog
                mock_context = self.get_context_from_user(context_needed, image_path)
                if mock_context is None:  # User cancelled
                    return
            
            # Test the stage
            if mock_context:
                result = tester.test_stage_with_mock_context(stage_name, image_path, mock_context)
            else:
                result = tester.test_stage(stage_name, image_path)
            
            # Show results
            self.show_stage_results(image_path, stage_name, result)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to test stage {stage_name}: {str(e)}")
    
    def test_all_stages(self, image_path):
        """Test all pipeline stages in sequence on the given image."""
        try:
            # Import stage tester
            from tests.test_single_stage import SingleStageTester
            
            # Create tester
            tester = SingleStageTester()
            
            # Test all stages
            all_stages = tester.get_available_stages()
            results = tester.test_stage_sequence(image_path, all_stages)
            
            # Show results
            self.show_all_stages_results(image_path, results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to test all stages: {str(e)}")
    
    def get_stage_context_requirements(self, stage_name):
        """Get context requirements for a specific stage."""
        context_requirements = {
            "aruco_check": None,  # No context needed
            "orientation_check": None,  # No context needed
            "roll_number_extraction": {
                "rotated_image_path": "Path to rotated image (optional)",
                "detected_markers": "List of detected marker IDs (optional)"
            },
            "omr_processing": {
                "detected_markers": "List of detected marker IDs",
                "roll_number": "Extracted roll number",
                "rotated_image_path": "Path to rotated image (optional)"
            },
            "api_upload": {
                "omr_data": "OMR processing data dictionary"
            }
        }
        
        return context_requirements.get(stage_name)
    
    def get_context_from_user(self, context_requirements, image_path):
        """Show dialog to get context data from user."""
        dialog = ContextInputDialog(context_requirements, image_path, self)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_context_data()
        return None
    
    def convert_numpy_types(self, obj):
        """Convert NumPy types to Python native types for JSON serialization."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, list):
            return [self.convert_numpy_types(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.convert_numpy_types(value) for key, value in obj.items()}
        else:
            return obj
    
    def show_stage_results(self, image_path, stage_name, result):
        """Show results of a single stage test."""
        filename = os.path.basename(image_path)
        
        if result['success']:
            # Show success message with details
            details = []
            for key, value in result.items():
                if key not in ['success', 'stage_name', 'stage_description']:
                    # Convert NumPy types to native Python types
                    converted_value = self.convert_numpy_types(value)
                    
                    if isinstance(converted_value, (list, dict)):
                        try:
                            details.append(f"{key}: {json.dumps(converted_value, indent=2)}")
                        except (TypeError, ValueError):
                            details.append(f"{key}: {str(converted_value)}")
                    else:
                        details.append(f"{key}: {converted_value}")
            
            details_text = "\n".join(details) if details else "Stage completed successfully"
            
            QMessageBox.information(
                self, 
                f"✅ {stage_name} - Success", 
                f"Stage '{stage_name}' completed successfully for {filename}!\n\n{details_text}"
            )
        else:
            # Show error message
            error_msg = result.get('error', 'Unknown error')
            QMessageBox.warning(
                self, 
                f"❌ {stage_name} - Failed", 
                f"Stage '{stage_name}' failed for {filename}:\n\n{error_msg}"
            )
    
    def show_all_stages_results(self, image_path, results):
        """Show results of all stages test."""
        filename = os.path.basename(image_path)
        
        # Count successes and failures
        success_count = sum(1 for result in results.values() if result and result.get('success', False))
        failure_count = len(results) - success_count
        
        # Create detailed results text
        details = []
        for stage_name, result in results.items():
            if result and result.get('success', False):
                details.append(f"✅ {stage_name}: Success")
            else:
                error = result.get('error', 'Unknown error') if result else 'Not run'
                details.append(f"❌ {stage_name}: {error}")
        
        details_text = "\n".join(details)
        
        QMessageBox.information(
            self, 
            f"📊 All Stages Results - {filename}", 
            f"Pipeline testing completed for {filename}!\n\n"
            f"✅ Successful: {success_count}\n"
            f"❌ Failed: {failure_count}\n"
            f"📊 Total: {len(results)}\n\n"
            f"Detailed Results:\n{details_text}"
        )


class ContextInputDialog(QDialog):
    """Dialog for inputting context data for pipeline stages."""
    
    def __init__(self, context_requirements, image_path, parent=None):
        super().__init__(parent)
        self.context_requirements = context_requirements
        self.image_path = image_path
        self.context_data = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Enter Context Data")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Context required for: {os.path.basename(self.image_path)}")
        header_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel(
            "Enter the required context data. You can use JSON format for complex data.\n"
            "Leave empty if not needed."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Context input fields
        self.input_fields = {}
        for field_name, description in self.context_requirements.items():
            field_layout = QHBoxLayout()
            
            # Label
            label = QLabel(f"{field_name}:")
            label.setMinimumWidth(150)
            field_layout.addWidget(label)
            
            # Input field
            if field_name in ["detected_markers", "omr_data"]:
                # Use text edit for complex data
                text_edit = QTextEdit()
                text_edit.setMaximumHeight(80)
                text_edit.setPlaceholderText(f"Enter {description} (JSON format)")
                self.input_fields[field_name] = text_edit
                field_layout.addWidget(text_edit)
            else:
                # Use line edit for simple data
                line_edit = QLineEdit()
                line_edit.setPlaceholderText(f"Enter {description}")
                self.input_fields[field_name] = line_edit
                field_layout.addWidget(line_edit)
            
            layout.addLayout(field_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def get_context_data(self):
        """Get the context data from the dialog."""
        context_data = {}
        
        for field_name, widget in self.input_fields.items():
            if isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            else:
                value = widget.text().strip()
            
            if value:
                # Try to parse as JSON if it looks like JSON
                if value.startswith('{') or value.startswith('['):
                    try:
                        context_data[field_name] = json.loads(value)
                    except json.JSONDecodeError:
                        context_data[field_name] = value
                else:
                    context_data[field_name] = value
        
        return context_data