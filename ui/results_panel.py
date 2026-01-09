import os
import shutil
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QGridLayout, QTextEdit, QTabWidget, QPushButton,
    QProgressBar, QMessageBox, QFileDialog, QCheckBox, QSpinBox,
    QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QThread, pyqtSignal
from typing import Dict
from PyQt5.QtGui import QPixmap, QFont
from PIL import Image
from PIL.ExifTags import TAGS

try:
    from image_processor import ImageProcessor, ALL_DEPENDENCIES_AVAILABLE
    OPENCV_AVAILABLE = ALL_DEPENDENCIES_AVAILABLE
except ImportError as e:
    ALL_DEPENDENCIES_AVAILABLE = False
    OPENCV_AVAILABLE = False
    print(f"Warning: ImageProcessor not available - {e}")


class ArUcoProcessingWorker(QThread):
    """Worker thread for processing images with ArUco marker detection and OCR"""
    progress_updated = pyqtSignal(int, str)  # progress, current_file
    processing_finished = pyqtSignal(dict)  # results dictionary
    file_processed = pyqtSignal(dict)  # individual file result
    status_message = pyqtSignal(str)  # detailed status messages for logging
    
    def __init__(self, source_folder, output_folder, expected_markers):
        super().__init__()
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.expected_markers = expected_markers
        self.is_cancelled = False
        self.processor = ImageProcessor() if ALL_DEPENDENCIES_AVAILABLE else None
        
    def cancel_processing(self):
        self.is_cancelled = True
        
    def run(self):
        """Main ArUco processing loop"""
        try:
            self.status_message.emit("🔄 Initializing ArUco processing...")
            
            if not ALL_DEPENDENCIES_AVAILABLE:
                self.status_message.emit("❌ ERROR: Required dependencies not available")
                error_msg = "Missing dependencies. "
                if not OPENCV_AVAILABLE:
                    error_msg += "Please install: pip install opencv-python pytesseract numpy"
                self.processing_finished.emit({
                    'total': 0, 'success': 0, 'failure': 0,
                    'message': error_msg
                })
                return
            
            self.status_message.emit("✅ All dependencies loaded successfully")
            
            # Set expected markers
            self.status_message.emit(f"🎯 Setting expected ArUco markers: {self.expected_markers}")
            self.processor.set_expected_markers(self.expected_markers)
            
            # Create success and failure folders directly in source folder
            self.status_message.emit("📁 Creating output directories...")
            # Create success and failure folders
            success_folder = os.path.join(self.source_folder, "success")
            failure_folder = os.path.join(self.source_folder, "failure")
            os.makedirs(success_folder, exist_ok=True)
            os.makedirs(failure_folder, exist_ok=True)
            self.status_message.emit(f"📁 Success folder: {success_folder}")
            self.status_message.emit(f"📁 Failure folder: {failure_folder}")
            
            # Get all image files (top-level only, no subdirectories)
            self.status_message.emit("🔍 Scanning for image files (top-level only)...")
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            image_files = []
            
            # Only scan top-level directory
            try:
                for file in os.listdir(self.source_folder):
                    file_path = os.path.join(self.source_folder, file)
                    if os.path.isfile(file_path):
                        if os.path.splitext(file.lower())[1] in image_extensions:
                            image_files.append(file_path)
            except Exception as e:
                self.status_message.emit(f"⚠️ Error scanning folder: {str(e)}")
            
            total_files = len(image_files)
            self.status_message.emit(f"📊 Found {total_files} image files to process")
            
            if total_files == 0:
                self.status_message.emit("⚠️ No image files found in the selected folder")
                self.processing_finished.emit({
                    'total': 0, 'success': 0, 'failure': 0,
                    'message': 'No image files found in the selected folder.'
                })
                return
            
            success_count = 0
            failure_count = 0
            processed_files = []
            
            self.status_message.emit("🚀 Starting batch processing...")
            
            # Process each image
            for i, image_path in enumerate(image_files):
                if self.is_cancelled:
                    self.status_message.emit("🛑 Processing cancelled by user")
                    break
                
                filename = os.path.basename(image_path)
                current_progress = int((i / total_files) * 100)
                
                self.status_message.emit(f"📷 [{i+1}/{total_files}] Processing: {filename}")
                self.progress_updated.emit(current_progress, f"Processing: {filename}")
                
                # Process image with ArUco detection and OCR
                self.status_message.emit(f"🔍 Detecting ArUco markers in {filename}...")
                result = self.processor.process_image(image_path, self.output_folder)
                
                # Log detection results
                detection_info = result['detection_info']
                detected_ids = detection_info.get('detected_ids', [])
                missing_ids = detection_info.get('missing_ids', [])
                
                if result['success']:
                    success_count += 1
                    self.status_message.emit(f"✅ {filename}: All markers found - {detected_ids}")
                else:
                    failure_count += 1
                    self.status_message.emit(f"❌ {filename}: Missing markers - {missing_ids}")
                
                # Log OCR results if available
                extracted_text = result.get('extracted_text', '')
                if extracted_text and extracted_text != "OCR Error: ":
                    text_preview = extracted_text[:50] + "..." if len(extracted_text) > 50 else extracted_text
                    self.status_message.emit(f"📝 {filename}: OCR extracted text - '{text_preview}'")
                
                # Log file operations
                if result.get('annotation_created', False):
                    self.status_message.emit(f"🖼️ {filename}: Annotated image created")
                
                processed_files.append(result)
                self.file_processed.emit(result)
            
            # Final results
            self.status_message.emit("📊 Processing completed! Generating final report...")
            results = {
                'total': total_files,
                'success': success_count,
                'failure': failure_count,
                'processed_files': processed_files,
                'message': f'Processing completed! {success_count} success, {failure_count} failure out of {total_files} files.'
            }
            
            self.status_message.emit(f"🎉 Final Results: {success_count} success, {failure_count} failure out of {total_files} files")
            self.status_message.emit(f"📈 Success rate: {(success_count/total_files*100):.1f}%" if total_files > 0 else "Success rate: 0%")
            
            self.processing_finished.emit(results)
            
        except Exception as e:
            error_msg = f"💥 CRITICAL ERROR during pipeline processing: {str(e)}"
            self.status_message.emit(error_msg)
            results = {
                'total': 0, 'success': 0, 'failure': 0,
                'message': f'Error during pipeline processing: {str(e)}'
            }
            self.processing_finished.emit(results)


class ProcessingLogDialog(QDialog):
    """Dialog showing real-time processing logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pipeline Processing Log")
        self.setMinimumSize(800, 600)
        self.setModal(False)  # Non-modal so user can see it during processing
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("🔄 Pipeline Processing in Progress...")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Status indicator
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)  # Disabled during processing
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Keep reference to this dialog
        self.setAttribute(Qt.WA_DeleteOnClose, False)
    
    def add_log(self, message):
        """Add a log message to the dialog"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        # Process events to update UI immediately
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
    
    def update_progress(self, value, text=""):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        if text:
            self.progress_bar.setFormat(f"{text} - %p%")
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
    
    def set_status(self, status, color="#2196F3"):
        """Update status label"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
    
    def processing_complete(self):
        """Called when processing is complete"""
        self.set_status("✅ Processing Complete!", "#4CAF50")
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Complete - 100%")
        self.close_button.setEnabled(True)
        self.add_log("\n" + "="*80)
        self.add_log("✅ PROCESSING COMPLETED SUCCESSFULLY!")
        self.add_log("="*80)
    
    def processing_error(self, error_msg):
        """Called when processing encounters an error"""
        self.set_status("❌ Processing Error", "#f44336")
        self.close_button.setEnabled(True)
        self.add_log("\n" + "="*80)
        self.add_log(f"❌ PROCESSING ERROR: {error_msg}")
        self.add_log("="*80)


class PipelineParametersDialog(QDialog):
    """Dialog for selecting pipeline processing parameters"""
    
    def __init__(self, parent=None, initial_values=None):
        super().__init__(parent)
        self.setWindowTitle("Pipeline Processing Parameters")
        # Make dialog 25% bigger: 400 * 1.25 = 500
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Zone mapping based on tenant
        self.zone_mapping = {
            'c2023-jgm': ['JAMB', 'GOP2', 'NAYA', 'GOP1', 'BIN1', 'BIN2', 'JGMM', 'JGMR', 'SANK'],
            'c2025-brb': ['RAMP', 'DBRJ', 'SURI-I', 'AHMD', 'SNTH', 'MHDB', 'KIRN', 'PAKR', 'NLHT', 'MRRI', 'ILMB', 'MYRS', 'BOLP', 'SURII', 'SURI-II']
        }
        
        # Default values
        initial_values = initial_values or {}
        default_tenant = initial_values.get('tenant', 'c2023-jgm')
        default_zone = initial_values.get('zone', '')
        default_class = initial_values.get('class_number', 1)
        default_year = initial_values.get('year', 2025)
        default_num_questions = initial_values.get('num_questions', 50)
        default_max_marks = initial_values.get('max_marks', 100)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)  # Increased spacing
        
        # Font size 25% bigger (default is ~9pt, so 25% bigger is ~11.25pt, round to 11pt)
        font = QFont()
        font.setPointSize(11)
        
        # Container for form fields
        form_container = QVBoxLayout()
        form_container.setSpacing(15)
        
        # Helper function to create a row with left-aligned label and right-aligned combo
        def create_form_row(label_text, combo_widget):
            row_layout = QHBoxLayout()
            label = QLabel(label_text + ":")
            label.setFont(font)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setMinimumWidth(180)  # Fixed width for labels
            combo_widget.setFont(font)
            combo_widget.setMinimumWidth(200)  # Minimum width for combo boxes
            row_layout.addWidget(label)
            row_layout.addStretch()  # Push combo to the right
            row_layout.addWidget(combo_widget)
            return row_layout
        
        # Year dropdown (FIRST)
        self.year_combo = QComboBox()
        self.year_combo.addItems(['2023', '2024', '2025'])
        self.year_combo.setCurrentText(str(default_year))
        self.year_combo.currentTextChanged.connect(self._update_roll_number_prefix)
        form_container.addLayout(create_form_row("Year", self.year_combo))
        
        # Tenant dropdown
        self.tenant_combo = QComboBox()
        self.tenant_combo.addItems(['c2023-jgm', 'c2025-brb'])
        self.tenant_combo.setCurrentText(default_tenant)
        self.tenant_combo.currentTextChanged.connect(self._on_tenant_changed)
        form_container.addLayout(create_form_row("Select Tenant", self.tenant_combo))
        
        # Zone dropdown
        self.zone_combo = QComboBox()
        self._update_zone_options(default_tenant)
        if default_zone and default_zone in [self.zone_combo.itemText(i) for i in range(self.zone_combo.count())]:
            self.zone_combo.setCurrentText(default_zone)
        self.zone_combo.currentTextChanged.connect(self._update_roll_number_prefix)
        form_container.addLayout(create_form_row("Select Zone", self.zone_combo))
        
        # Class number dropdown (pad with leading zero for single digits)
        self.class_combo = QComboBox()
        self.class_combo.addItems([f"{i:02d}" for i in range(1, 11)])
        # Convert default_class to string with zero padding for matching
        default_class_str = f"{default_class:02d}"
        self.class_combo.setCurrentText(default_class_str)
        self.class_combo.currentTextChanged.connect(self._update_roll_number_prefix)
        form_container.addLayout(create_form_row("Class Number", self.class_combo))
        
        # Expected Roll Number Prefix (display only, auto-generated)
        self.roll_prefix_label = QLabel()
        self.roll_prefix_label.setFont(font)
        self.roll_prefix_label.setStyleSheet("color: #666; font-style: italic;")
        self._update_roll_number_prefix()  # Initial calculation
        form_container.addLayout(create_form_row("Expected Roll Number Prefix", self.roll_prefix_label))
        
        # Number of questions dropdown (1-100)
        self.num_questions_combo = QComboBox()
        self.num_questions_combo.addItems([str(i) for i in range(1, 101)])
        self.num_questions_combo.setCurrentText(str(default_num_questions))
        form_container.addLayout(create_form_row("Number of Questions", self.num_questions_combo))
        
        # Maximum marks dropdown (1-100)
        self.max_marks_combo = QComboBox()
        self.max_marks_combo.addItems([str(i) for i in range(1, 101)])
        self.max_marks_combo.setCurrentText(str(default_max_marks))
        form_container.addLayout(create_form_row("Maximum Marks", self.max_marks_combo))
        
        layout.addLayout(form_container)
        layout.addStretch()
        
        # Dialog buttons with larger font
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.setFont(font)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_tenant_changed(self, tenant):
        """Update zone options when tenant changes"""
        current_zone = self.zone_combo.currentText()
        self._update_zone_options(tenant)
        # Try to keep the same zone if it exists in the new list
        if current_zone in [self.zone_combo.itemText(i) for i in range(self.zone_combo.count())]:
            self.zone_combo.setCurrentText(current_zone)
        # Update roll number prefix when tenant/zone changes
        self._update_roll_number_prefix()
    
    def _update_zone_options(self, tenant):
        """Update zone combo box based on tenant"""
        self.zone_combo.clear()
        zones = self.zone_mapping.get(tenant, [])
        self.zone_combo.addItems(zones)
    
    def _update_roll_number_prefix(self):
        """Calculate and update the expected roll number prefix"""
        zone = self.zone_combo.currentText()
        year = self.year_combo.currentText()
        class_num = self.class_combo.currentText()
        
        if zone and year and class_num:
            # Format: <zone><year two digit><class two digit>
            # Year is 4 digits (e.g., "2025"), take last 2 digits for prefix
            year_two_digit = year[-2:] if len(year) == 4 else year
            # Class is already zero-padded (e.g., "01", "02")
            prefix = f"{zone}{year_two_digit}{class_num}"
            self.roll_prefix_label.setText(prefix)
        else:
            self.roll_prefix_label.setText("--")
    
    def get_parameters(self):
        """Get the selected parameters"""
        # Convert class number back to int (it's stored as "01", "02", etc. in dropdown)
        class_text = self.class_combo.currentText()
        class_number = int(class_text)  # Will correctly parse "01" as 1, "02" as 2, etc.
        
        # Calculate expected roll number prefix
        zone = self.zone_combo.currentText()
        year = self.year_combo.currentText()
        year_two_digit = year[-2:]
        class_two_digit = class_text  # Already zero-padded
        expected_roll_number_prefix = f"{zone}{year_two_digit}{class_two_digit}"
        
        return {
            'tenant': self.tenant_combo.currentText(),
            'zone': self.zone_combo.currentText(),
            'class_number': class_number,
            'year': int(self.year_combo.currentText()),
            'num_questions': int(self.num_questions_combo.currentText()),
            'max_marks': int(self.max_marks_combo.currentText()),
            'expected_roll_number_prefix': expected_roll_number_prefix
        }


class PipelineProcessingWorker(QThread):
    """Worker thread for comprehensive pipeline processing of images"""
    progress_updated = pyqtSignal(int, str)  # progress, current_file
    processing_finished = pyqtSignal(dict)  # results dictionary
    file_processed = pyqtSignal(dict)  # individual file result
    status_message = pyqtSignal(str)  # detailed status messages for logging
    
    def __init__(self, source_folder, output_folder, expected_markers, pipeline_parameters=None):
        super().__init__()
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.expected_markers = expected_markers
        self.pipeline_parameters = pipeline_parameters or {}
        self.is_cancelled = False
        self.processor = ImageProcessor() if ALL_DEPENDENCIES_AVAILABLE else None
        
    def cancel_processing(self):
        self.is_cancelled = True
        
    def run(self):
        """Main pipeline processing loop"""
        try:
            self.status_message.emit("🔄 Initializing pipeline processing...")
            
            if not ALL_DEPENDENCIES_AVAILABLE:
                self.status_message.emit("❌ ERROR: Required dependencies not available")
                error_msg = "Missing dependencies. "
                if not OPENCV_AVAILABLE:
                    error_msg += "Please install: pip install opencv-python pytesseract numpy"
                self.processing_finished.emit({
                    'total': 0, 'success': 0, 'failure': 0,
                    'message': error_msg
                })
                return
            
            self.status_message.emit("✅ All dependencies loaded successfully")
            
            # Set expected markers
            self.status_message.emit(f"🎯 Setting expected ArUco markers: {self.expected_markers}")
            self.processor.set_expected_markers(self.expected_markers)
            
            # Use the source folder directly for success/error folders
            # No need for nested pipeline_results structure
            self.status_message.emit("📁 Using source folder for output...")
            
            # Create success and error folders directly in source folder
            success_folder = os.path.join(self.source_folder, "success")
            error_folder = os.path.join(self.source_folder, "error")
            os.makedirs(success_folder, exist_ok=True)
            os.makedirs(error_folder, exist_ok=True)
            self.status_message.emit(f"📁 Success folder: {success_folder}")
            self.status_message.emit(f"📁 Error folder: {error_folder}")
            
            # Get all image files (top-level only, no subdirectories)
            self.status_message.emit("🔍 Scanning for image files (top-level only)...")
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            image_files = []
            
            # Only scan top-level directory
            try:
                for file in os.listdir(self.source_folder):
                    file_path = os.path.join(self.source_folder, file)
                    if os.path.isfile(file_path):
                        if os.path.splitext(file.lower())[1] in image_extensions:
                            image_files.append(file_path)
            except Exception as e:
                self.status_message.emit(f"⚠️ Error scanning folder: {str(e)}")
            
            total_files = len(image_files)
            self.status_message.emit(f"📊 Found {total_files} image files to process")
            
            if total_files == 0:
                self.status_message.emit("⚠️ No image files found in the selected folder")
                self.processing_finished.emit({
                    'total': 0, 'success': 0, 'failure': 0,
                    'message': 'No image files found in the selected folder.'
                })
                return
            
            success_count = 0
            failure_count = 0
            processed_files = []
            
            self.status_message.emit("🚀 Starting pipeline processing...")
            
            # Process each image through the pipeline
            for i, image_path in enumerate(image_files):
                if self.is_cancelled:
                    self.status_message.emit("🛑 Processing cancelled by user")
                    break
                
                filename = os.path.basename(image_path)
                current_progress = int((i / total_files) * 100)
                
                self.status_message.emit(f"📷 [{i+1}/{total_files}] Processing: {filename}")
                self.progress_updated.emit(current_progress, f"Processing: {filename}")
                
                # Process image through the comprehensive pipeline
                self.status_message.emit(f"🔧 Running pipeline for {filename}...")
                result = self.processor.process_image_pipeline(
                    image_path, self.source_folder, self.pipeline_parameters
                )
                
                # Log pipeline results
                if result['success']:
                    success_count += 1
                    stages = result.get('stages', {})
                    stage_summary = []
                    for stage_name, stage_result in stages.items():
                        if stage_result.get('success'):
                            stage_summary.append(f"✅{stage_name}")
                        else:
                            stage_summary.append(f"❌{stage_name}")
                    
                    self.status_message.emit(f"✅ {filename}: Pipeline completed - {' '.join(stage_summary)}")
                    
                    # Log roll number if extracted
                    roll_number = result.get('stages', {}).get('roll_number_extraction', {}).get('roll_number')
                    if roll_number:
                        self.status_message.emit(f"🆔 {filename}: Roll Number - {roll_number}")
                    
                    # Log API upload status
                    if result.get('api_upload_success'):
                        upload_id = result.get('stages', {}).get('api_upload', {}).get('upload_id')
                        self.status_message.emit(f"📤 {filename}: Uploaded to API - {upload_id}")
                else:
                    failure_count += 1
                    error_stage = result.get('error_stage', 'unknown')
                    error_message = result.get('error_message', 'Unknown error')
                    self.status_message.emit(f"❌ {filename}: Failed at {error_stage} - {error_message}")
                
                processed_files.append(result)
                self.file_processed.emit(result)
            
            # Final results
            self.status_message.emit("📊 Pipeline processing completed! Generating final report...")
            results = {
                'total': total_files,
                'success': success_count,
                'failure': failure_count,
                'processed_files': processed_files,
                'message': f'Pipeline processing completed! {success_count} success, {failure_count} failure out of {total_files} files.'
            }
            
            self.status_message.emit(f"🎉 Final Results: {success_count} success, {failure_count} failure out of {total_files} files")
            self.status_message.emit(f"📈 Success rate: {(success_count/total_files*100):.1f}%" if total_files > 0 else "Success rate: 0%")
            
            self.processing_finished.emit(results)
            
        except Exception as e:
            error_msg = f"💥 CRITICAL ERROR during pipeline processing: {str(e)}"
            self.status_message.emit(error_msg)
            results = {
                'total': 0, 'success': 0, 'failure': 0,
                'message': f'Error during pipeline processing: {str(e)}'
            }
            self.processing_finished.emit(results)


class ResultsPanel(QWidget):
    # Signal to notify when a folder is loaded
    folder_loaded = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_folder = None
        self.current_image = None
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.next_scan_image)
        self.current_scan_index = 0
        self.scan_images_list = []
        self.is_scanning = False
        # Store pipeline parameters (persist across processing sessions)
        self.pipeline_parameters = {
            'tenant': 'c2023-jgm',
            'zone': 'JAMB',
            'class_number': 1,
            'year': 2025,
            'num_questions': 50,
            'max_marks': 100
        }
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Auto-load default folder for development
        QTimer.singleShot(100, self.load_default_folder)
        
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
        
        # Title and buttons layout
        title_button_layout = QHBoxLayout()
        
        title = QLabel("📊 Analysis Results")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.scan_button = QPushButton("🔍 Scan All Images")
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.scan_button.clicked.connect(self.start_scan_all_images)
        
        self.upload_button = QPushButton("⬆️ Upload Results")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.upload_button.clicked.connect(self.upload_results)
        
        self.process_aruco_button = QPushButton("🎯 Process ArUco Images")
        self.process_aruco_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6600;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e55a00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.process_aruco_button.clicked.connect(self.start_aruco_processing)
        if not ALL_DEPENDENCIES_AVAILABLE:
            self.process_aruco_button.setEnabled(False)
            self.process_aruco_button.setToolTip("Required dependencies not available. Install opencv-python, pytesseract, and numpy.")

        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.process_aruco_button)
        button_layout.addStretch()
        
        title_button_layout.addWidget(title)
        title_button_layout.addStretch()
        title_button_layout.addLayout(button_layout)
        
        header_layout.addLayout(title_button_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3f72af;
            }
        """)

        # ArUco Processing Tab (make this the first tab)
        self.aruco_tab = self.create_aruco_processing_tab()
        self.tab_widget.addTab(self.aruco_tab, "🎯 ArUco Processing")

        # Processing Log Tab
        self.processing_log_tab = self.create_processing_log_tab()
        self.tab_widget.addTab(self.processing_log_tab, "📋 Processing Log")

        # Folder Overview Tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "� Folder Overview")

        # Image Details Tab
        self.details_tab = self.create_details_tab()
        self.tab_widget.addTab(self.details_tab, "🖼️ Image Details")

        # Uploaded Results Tab (initially hidden)
        self.uploaded_results_tab = None
        self.uploaded_results_tab_index = None

        # Add widgets to main layout
        layout.addWidget(header_frame)
        layout.addWidget(self.tab_widget)

        # Set ArUco Processing tab as the default visible tab
        self.tab_widget.setCurrentIndex(0)
        
        
    def create_overview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Folder statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #dee2e6;
            }
        """)
        stats_layout = QGridLayout(stats_frame)
        
        # Statistics labels
        self.total_images_label = QLabel("0")
        self.total_size_label = QLabel("0 B")
        self.avg_size_label = QLabel("0 B")
        self.formats_label = QLabel("None")
        
        # Style the stat values
        for label in [self.total_images_label, self.total_size_label, 
                     self.avg_size_label, self.formats_label]:
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet("color: #2b7a78;")
        
        # Add to grid
        stats_layout.addWidget(QLabel("Total Images:"), 0, 0)
        stats_layout.addWidget(self.total_images_label, 0, 1)
        stats_layout.addWidget(QLabel("Total Size:"), 1, 0)
        stats_layout.addWidget(self.total_size_label, 1, 1)
        stats_layout.addWidget(QLabel("Average Size:"), 2, 0)
        stats_layout.addWidget(self.avg_size_label, 2, 1)
        stats_layout.addWidget(QLabel("Formats:"), 3, 0)
        stats_layout.addWidget(self.formats_label, 3, 1)
        
        # Format breakdown
        breakdown_frame = QFrame()
        breakdown_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #dee2e6;
            }
        """)
        breakdown_layout = QVBoxLayout(breakdown_frame)
        
        breakdown_title = QLabel("📈 Format Breakdown")
        breakdown_title.setFont(QFont("Arial", 12, QFont.Bold))
        breakdown_layout.addWidget(breakdown_title)
        
        self.format_breakdown = QLabel("No data available")
        self.format_breakdown.setStyleSheet("color: #666; margin-top: 10px;")
        self.format_breakdown.setWordWrap(True)
        breakdown_layout.addWidget(self.format_breakdown)
        
        layout.addWidget(stats_frame)
        layout.addWidget(breakdown_frame)
        layout.addStretch()
        
        return widget
        
    def create_details_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Image preview (80% of height)
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #dee2e6;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_title = QLabel("🖼️ Preview")
        preview_title.setFont(QFont("Arial", 12, QFont.Bold))
        preview_layout.addWidget(preview_title)
        
        # Scroll area for image - make it much taller
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        scroll_area.setMinimumHeight(400)  # Much taller preview
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("No image selected")
        self.image_preview.setStyleSheet("padding: 20px; color: #666;")
        scroll_area.setWidget(self.image_preview)
        
        preview_layout.addWidget(scroll_area)
        
        # Image properties (docked at bottom)
        props_frame = QFrame()
        props_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #dee2e6;
            }
        """)
        props_layout = QVBoxLayout(props_frame)
        
        props_title = QLabel("📋 Properties")
        props_title.setFont(QFont("Arial", 12, QFont.Bold))
        props_layout.addWidget(props_title)
        
        self.image_properties = QTextEdit()
        self.image_properties.setMaximumHeight(150)  # Smaller properties section
        self.image_properties.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.image_properties.setPlainText("No image selected")
        props_layout.addWidget(self.image_properties)
        
        # Set stretch factors to give preview 80% and properties 20%
        layout.addWidget(preview_frame, 4)  # 80% of space
        layout.addWidget(props_frame, 1)    # 20% of space
        
        return widget
        
    def create_aruco_processing_tab(self):
        """Create the ArUco marker processing configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Configuration Section
        config_group = QGroupBox("🎯 ArUco Marker Configuration")
        config_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        config_layout = QFormLayout(config_group)
        
        # Expected marker IDs input
        marker_layout = QVBoxLayout()
        

        # Create four rows of checkboxes (5 markers each, for 1-20)
        marker_rows = [QHBoxLayout() for _ in range(4)]
        self.marker_checkboxes = []
        for i in range(1, 21):  # Markers 1 to 20
            checkbox = QCheckBox(f"Marker {i}")
            checkbox.setChecked(True)
            self.marker_checkboxes.append(checkbox)
            row_idx = (i - 1) // 5
            marker_rows[row_idx].addWidget(checkbox)
        for row in marker_rows:
            row.addStretch()
            marker_layout.addLayout(row)

        config_layout.addRow("Expected Markers:", marker_layout)
        
        # Add info about ArUco format
        format_info_label = QLabel("Using ArUco DICT_4X4_50 format (Valid IDs: 0-49)")
        format_info_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        config_layout.addRow("", format_info_label)
        
        # Processing options
        self.ocr_enabled_checkbox = QCheckBox("Enable OCR Text Extraction")
        self.ocr_enabled_checkbox.setChecked(True)
        config_layout.addRow("OCR Options:", self.ocr_enabled_checkbox)
        
        layout.addWidget(config_group)
        
        # Pipeline Processing Section
        pipeline_group = QGroupBox("🔧 Pipeline Processing")
        pipeline_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        pipeline_layout = QVBoxLayout(pipeline_group)
        
        # Pipeline description
        pipeline_desc = QLabel("""
        Comprehensive pipeline processing:
        1. ✅ Check ArUco markers presence
        2. 🔄 Check and rotate tilted images  
        3. 🆔 Extract exam roll number
        4. 📝 Process OMR sheet
        5. 📤 Upload to API
        """)
        pipeline_desc.setStyleSheet("color: #666; font-size: 11px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;")
        pipeline_layout.addWidget(pipeline_desc)
        
        # Pipeline processing button
        self.process_pipeline_button = QPushButton("🚀 Start Pipeline Processing")
        self.process_pipeline_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 12px 20px;
                border-radius: 5px;
                font-size: 14px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.process_pipeline_button.clicked.connect(self.start_pipeline_processing)
        if not ALL_DEPENDENCIES_AVAILABLE:
            self.process_pipeline_button.setEnabled(False)
            self.process_pipeline_button.setToolTip("Required dependencies not available. Install opencv-python, pytesseract, and numpy.")
        
        pipeline_layout.addWidget(self.process_pipeline_button)
        
        layout.addWidget(pipeline_group)
        
        # Thumbnail Viewers Section
        from .thumbnail_viewer import ThumbnailViewer
        
        # Success thumbnails
        self.success_thumbnail_viewer = ThumbnailViewer("✅ Success Results", "#28a745")
        self.success_thumbnail_viewer.thumbnail_clicked.connect(self.show_image_popup)
        layout.addWidget(self.success_thumbnail_viewer)
        
        # Error thumbnails
        self.error_thumbnail_viewer = ThumbnailViewer("❌ Error Results", "#dc3545")
        self.error_thumbnail_viewer.thumbnail_clicked.connect(self.show_image_popup)
        layout.addWidget(self.error_thumbnail_viewer)
        
        # Processing Status Section
        status_group = QGroupBox("📊 Processing Status")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        status_layout = QVBoxLayout(status_group)
        
        # Progress bar
        self.aruco_progress_bar = QProgressBar()
        self.aruco_progress_bar.setVisible(False)
        status_layout.addWidget(self.aruco_progress_bar)
        
        # Status label
        self.aruco_status_label = QLabel("Ready to process images")
        self.aruco_status_label.setStyleSheet("color: #666; padding: 10px;")
        status_layout.addWidget(self.aruco_status_label)
        
        # Results text area
        self.aruco_results_text = QTextEdit()
        self.aruco_results_text.setMaximumHeight(200)
        self.aruco_results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.aruco_results_text.setPlainText("Processing results will appear here...")
        status_layout.addWidget(self.aruco_results_text)
        
        # Add a table below the Processing Status to list file names and detected ArUco markers with midpoints
        # Create table widget
        self.aruco_results_table = QTableWidget()
        self.aruco_results_table.setColumnCount(21)  # 1 for file name, 20 for markers
        self.aruco_results_table.setHorizontalHeaderLabels(["File Name"] + [f"Marker {i}" for i in range(1, 21)])
        self.aruco_results_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-family: 'Arial';
                font-size: 12px;
            }
        """)

        # Add table to layout
        status_layout.addWidget(self.aruco_results_table)

        # Add an aggregated view below the ArUco results table
        self.aruco_aggregated_table = QTableWidget()
        self.aruco_aggregated_table.setColumnCount(3)  # Marker ID, Mean X, Mean Y
        self.aruco_aggregated_table.setHorizontalHeaderLabels(["Marker ID", "Mean X", "Mean Y"])
        self.aruco_aggregated_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-family: 'Arial';
                font-size: 12px;
            }
        """)

        # Add aggregated table to layout
        status_layout.addWidget(self.aruco_aggregated_table)

        layout.addWidget(status_group)
        
        # Removed the processing log and instruction section
        # layout.removeWidget(log_group)
        # log_group.deleteLater()
        # layout.removeWidget(instructions_label)
        # instructions_label.deleteLater()
        
        return widget
    
    # Create the processing log tab
    # This tab will be used to display the processing log and allow clearing it
    def create_processing_log_tab(self):
        """Create the processing log tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # Log title
        log_title = QLabel("📋 Processing Log")
        log_title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(log_title)
        
        # Processing log text area
        self.processing_log = QTextEdit()
        self.processing_log.setReadOnly(True)
        self.processing_log.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.processing_log)
        
        # Auto-scroll checkbox
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll to bottom")
        self.auto_scroll_checkbox.setChecked(True)
        layout.addWidget(self.auto_scroll_checkbox)
        
        return widget

    
    def start_aruco_processing(self):
        """Start ArUco marker processing for images"""
        if not ALL_DEPENDENCIES_AVAILABLE:
            QMessageBox.warning(self, "Dependencies Not Available", 
                              "Required dependencies are not available for ArUco processing.\n"
                              "Please install: pip install opencv-python pytesseract numpy\n\n"
                              "Note: You may need to fix numpy/pandas version conflicts.")
            return
        
        if not self.current_folder:
            QMessageBox.warning(self, "No Folder Selected", 
                              "Please select a folder with images first.")
            return
        # Use the current folder as the output folder automatically
        output_folder = self.current_folder
        
        # Get expected marker IDs from checkboxes (should be 1-based, not 0-based)
        expected_markers = []
        for i, checkbox in enumerate(self.marker_checkboxes, start=1):
            if checkbox.isChecked():
                expected_markers.append(i)
        
        if not expected_markers:
            QMessageBox.warning(self, "No Markers Selected", 
                              "Please select at least one expected ArUco marker.")
            return
        
        # Update UI
        self.process_aruco_button.setEnabled(False)
        self.aruco_progress_bar.setVisible(True)
        self.aruco_progress_bar.setValue(0)
        self.aruco_status_label.setText("Starting ArUco processing...")
        self.aruco_results_text.clear()
        
        # Start processing thread
        self.aruco_worker = ArUcoProcessingWorker(
            self.current_folder, output_folder, expected_markers
        )
        self.aruco_worker.progress_updated.connect(self.update_aruco_progress)
        self.aruco_worker.file_processed.connect(self.on_aruco_file_processed)
        self.aruco_worker.processing_finished.connect(self.on_aruco_processing_finished)
        self.aruco_worker.status_message.connect(self.add_to_processing_log)
        self.aruco_worker.start()
        
        # Clear the processing log and add initial message
        self.processing_log.clear()
        self.add_to_processing_log("🚀 ArUco processing started...")
    
    def start_pipeline_processing(self):
        """Start comprehensive pipeline processing"""
        if not ALL_DEPENDENCIES_AVAILABLE:
            QMessageBox.warning(self, "Dependencies Not Available", 
                              "Required dependencies are not available for pipeline processing.\n"
                              "Please install: pip install opencv-python pytesseract numpy\n\n"
                              "Note: You may need to fix numpy/pandas version conflicts.")
            return
        
        if not self.current_folder:
            QMessageBox.warning(self, "No Folder Selected", 
                              "Please select a folder with images first.")
            return
        
        # Show parameter dialog
        dialog = PipelineParametersDialog(self, self.pipeline_parameters)
        if dialog.exec_() != QDialog.Accepted:
            return  # User cancelled
        
        # Get and store parameters
        self.pipeline_parameters = dialog.get_parameters()
        
        # Get expected marker IDs from checkboxes
        expected_markers = []
        for i, checkbox in enumerate(self.marker_checkboxes, start=1):
            if checkbox.isChecked():
                expected_markers.append(i)
        
        if not expected_markers:
            QMessageBox.warning(self, "No Markers Selected", 
                              "Please select at least one expected ArUco marker.")
            return
        
        # Use current folder directly for output (success/error created there)
        # Update UI
        self.process_pipeline_button.setEnabled(False)
        self.process_aruco_button.setEnabled(False)  # Disable both buttons
        self.aruco_progress_bar.setVisible(True)
        self.aruco_progress_bar.setValue(0)
        self.aruco_status_label.setText("Starting pipeline processing...")
        self.aruco_results_text.clear()
        
        # Create and show processing log dialog
        self.processing_log_dialog = ProcessingLogDialog(self)
        self.processing_log_dialog.show()
        
        # Start pipeline processing thread - use current_folder as output folder
        self.pipeline_worker = PipelineProcessingWorker(
            self.current_folder, self.current_folder, expected_markers, self.pipeline_parameters
        )
        self.pipeline_worker.progress_updated.connect(self.update_aruco_progress)
        self.pipeline_worker.file_processed.connect(self.on_pipeline_file_processed)
        self.pipeline_worker.processing_finished.connect(self.on_pipeline_processing_finished)
        # Connect status messages to both the popup dialog and the main log
        self.pipeline_worker.status_message.connect(self.add_to_processing_log)
        self.pipeline_worker.status_message.connect(self.processing_log_dialog.add_log)
        # Connect progress to popup dialog
        self.pipeline_worker.progress_updated.connect(
            lambda progress, text: self.processing_log_dialog.update_progress(progress, text)
        )
        self.pipeline_worker.start()
        
        # Add initial messages to popup dialog
        self.processing_log_dialog.set_status("🔄 Processing...", "#2196F3")
        self.processing_log_dialog.add_log("🚀 Pipeline processing started...")
        self.processing_log_dialog.add_log(f"📋 Parameters:")
        self.processing_log_dialog.add_log(f"   Year: {self.pipeline_parameters['year']}")
        self.processing_log_dialog.add_log(f"   Tenant: {self.pipeline_parameters['tenant']}")
        self.processing_log_dialog.add_log(f"   Zone: {self.pipeline_parameters['zone']}")
        self.processing_log_dialog.add_log(f"   Class: {self.pipeline_parameters['class_number']}")
        self.processing_log_dialog.add_log(f"   Questions: {self.pipeline_parameters['num_questions']}")
        self.processing_log_dialog.add_log(f"   Max Marks: {self.pipeline_parameters['max_marks']}")
        self.processing_log_dialog.add_log("="*80)
        
        # Also add to main processing log
        self.processing_log.clear()
        self.add_to_processing_log("🚀 Pipeline processing started...")
        self.add_to_processing_log(f"📋 Parameters: Year={self.pipeline_parameters['year']}, "
                                   f"Tenant={self.pipeline_parameters['tenant']}, "
                                   f"Zone={self.pipeline_parameters['zone']}, "
                                   f"Class={self.pipeline_parameters['class_number']}, "
                                   f"Questions={self.pipeline_parameters['num_questions']}, "
                                   f"Max Marks={self.pipeline_parameters['max_marks']}")
    
    def clear_processing_log(self):
        """Clear the processing log"""
        self.processing_log.clear()
        self.add_to_processing_log("📋 Log cleared")
    
    def add_to_processing_log(self, message):
        """Add a timestamped message to the processing log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        log_entry = f"[{timestamp}] {message}"
        
        # Add to log
        self.processing_log.append(log_entry)
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_checkbox.isChecked():
            scrollbar = self.processing_log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def update_aruco_progress(self, progress, current_file):
        """Update ArUco processing progress"""
        self.aruco_progress_bar.setValue(progress)
        self.aruco_status_label.setText(f"Processing: {current_file}")
    
    def populate_aruco_results_table(self, results):
        """Populate the ArUco results table with processing results"""
        def to_int_tuple(val):
            # Convert tuple of np types to plain int
            if isinstance(val, (tuple, list)) and len(val) == 2:
                return (int(round(val[0])), int(round(val[1])))
            return ("NA", "NA")

        self.aruco_results_table.setRowCount(len(results))
        marker_ids = list(range(1, 21))
        for row, result in enumerate(results):
            file_name_item = QTableWidgetItem(result.get('filename', ''))
            self.aruco_results_table.setItem(row, 0, file_name_item)
            detection_info = result.get('detection_info', {})
            detected_ids = detection_info.get('detected_ids', [])
            midpoints = detection_info.get('marker_midpoints', [])
            for col, marker_id in enumerate(marker_ids, start=1):
                if marker_id in detected_ids:
                    idx = detected_ids.index(marker_id)
                    pt = midpoints[idx] if idx < len(midpoints) else ("NA", "NA")
                    x, y = to_int_tuple(pt)
                    midpoint_str = f"{x},{y}" if x != "NA" and y != "NA" else "NA"
                    self.aruco_results_table.setItem(row, col, QTableWidgetItem(midpoint_str))
                else:
                    self.aruco_results_table.setItem(row, col, QTableWidgetItem("NA"))

        # Populate aggregated table with mean values for all marker IDs 1-20
        aggregated_data = {marker_id: [] for marker_id in marker_ids}
        for result in results:
            detection_info = result.get('detection_info', {})
            detected_ids = detection_info.get('detected_ids', [])
            midpoints = detection_info.get('marker_midpoints', [])
            for marker_id in marker_ids:
                if marker_id in detected_ids:
                    idx = detected_ids.index(marker_id)
                    pt = midpoints[idx] if idx < len(midpoints) else ("NA", "NA")
                    x, y = to_int_tuple(pt)
                    if x != "NA" and y != "NA":
                        aggregated_data[marker_id].append((x, y))

        self.aruco_aggregated_table.setRowCount(len(marker_ids))
        for row, marker_id in enumerate(marker_ids):
            points = aggregated_data[marker_id]
            if points:
                mean_x = int(round(np.mean([p[0] for p in points])))
                mean_y = int(round(np.mean([p[1] for p in points])))
            else:
                mean_x = "NA"
                mean_y = "NA"
            self.aruco_aggregated_table.setItem(row, 0, QTableWidgetItem(str(marker_id)))
            self.aruco_aggregated_table.setItem(row, 1, QTableWidgetItem(str(mean_x)))
            self.aruco_aggregated_table.setItem(row, 2, QTableWidgetItem(str(mean_y)))
    
    def next_scan_image(self):
        """Scan the next image in the folder and update the UI."""
        if not self.scan_images_list or self.current_scan_index >= len(self.scan_images_list):
            self.scan_timer.stop()
            self.is_scanning = False
            self.aruco_status_label.setText("Scanning completed.")
            return

        current_image_path = self.scan_images_list[self.current_scan_index]
        self.current_scan_index += 1

        try:
            pixmap = QPixmap(current_image_path)
            self.image_preview.setPixmap(pixmap.scaled(
                self.image_preview.width(), self.image_preview.height(), Qt.KeepAspectRatio
            ))
            self.image_properties.setPlainText(f"Image: {current_image_path}\nSize: {pixmap.width()}x{pixmap.height()} pixels")
            self.aruco_status_label.setText(f"Scanning: {current_image_path}")
        except Exception as e:
            self.aruco_status_label.setText(f"Error scanning {current_image_path}: {str(e)}")

    def start_scan_all_images(self):
        """Start scanning all images in the selected folder."""
        if not self.current_folder:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder with images first.")
            return

        self.scan_images_list = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}

        for root, dirs, files in os.walk(self.current_folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    self.scan_images_list.append(os.path.join(root, file))

        if not self.scan_images_list:
            QMessageBox.warning(self, "No Images Found", "No valid images found in the selected folder.")
            return

        self.current_scan_index = 0
        self.is_scanning = True
        self.scan_timer.start(1000)  # Scan one image per second
        self.aruco_status_label.setText("Starting scan...")
        self.add_to_processing_log("🚀 Starting scan of all images...")
    
    def upload_results(self):
        """Export the ArUco results table and aggregated table to CSV files."""
        from PyQt5.QtWidgets import QFileDialog
        import csv

        # Ask user for export folder
        export_folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Results")
        if not export_folder:
            return

        # Export per-image results table
        per_image_csv = os.path.join(export_folder, "aruco_per_image_results.csv")
        with open(per_image_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            headers = [self.aruco_results_table.horizontalHeaderItem(i).text() for i in range(self.aruco_results_table.columnCount())]
            writer.writerow(headers)
            # Write rows
            for row in range(self.aruco_results_table.rowCount()):
                row_data = []
                for col in range(self.aruco_results_table.columnCount()):
                    item = self.aruco_results_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        # Export aggregated results table
        agg_csv = os.path.join(export_folder, "aruco_aggregated_results.csv")
        with open(agg_csv, mode="w", newline="") as f:
            writer = csv.writer(f)
            headers = [self.aruco_aggregated_table.horizontalHeaderItem(i).text() for i in range(self.aruco_aggregated_table.columnCount())]
            writer.writerow(headers)
            for row in range(self.aruco_aggregated_table.rowCount()):
                row_data = []
                for col in range(self.aruco_aggregated_table.columnCount()):
                    item = self.aruco_aggregated_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        QMessageBox.information(self, "Export Complete", f"Results exported to:\n{per_image_csv}\n{agg_csv}")
    
    def load_default_folder(self):
        """Load the default OMR_300DPI_pages folder for development."""
        default_folder = "test_input_pdf/OMR_300DPI_pages"
        
        if os.path.exists(default_folder):
            print(f"🚀 Auto-loading default folder: {default_folder}")
            self.analyze_folder(default_folder, recursive=False)
            # Emit signal to notify other components
            self.folder_loaded.emit(default_folder)
            # Update status to show default folder is loaded
            if hasattr(self, 'aruco_status_label'):
                self.aruco_status_label.setText(f"✅ Default folder loaded: {default_folder}")
        else:
            print(f"⚠️ Default folder not found: {default_folder}")
            if hasattr(self, 'aruco_status_label'):
                self.aruco_status_label.setText("⚠️ Default folder not found - please select a folder manually")
    
    def analyze_folder(self, folder_path, recursive=True):
        """Set the current folder, update the overview tab, and load all images in the left pane."""
        self.current_folder = folder_path
        
        # Clear thumbnail viewers when folder changes
        self.clear_thumbnail_viewers()
        
        # First, quickly scan for files without calculating sizes (to avoid UI freeze)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_files = []
        formats = set()
        
        if recursive:
            # Scan recursively (original behavior)
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file.lower())[1]
                    if ext in image_extensions:
                        image_files.append(os.path.join(root, file))
                        formats.add(ext)
        else:
            # Scan only current directory (for default folder)
            try:
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path):
                        ext = os.path.splitext(file.lower())[1]
                        if ext in image_extensions:
                            image_files.append(file_path)
                            formats.add(ext)
            except Exception as e:
                print(f"Error scanning folder {folder_path}: {e}")
        
        # Update UI immediately with file count (before calculating sizes)
        num_images = len(image_files)
        self.total_images_label.setText(str(num_images))
        self.formats_label.setText(", ".join(sorted(formats)) if formats else "None")
        
        # Format breakdown
        breakdown = {}
        for file in image_files:
            ext = os.path.splitext(file.lower())[1]
            breakdown[ext] = breakdown.get(ext, 0) + 1
        if breakdown:
            breakdown_str = ", ".join([f"{k}: {v}" for k, v in sorted(breakdown.items())])
            self.format_breakdown.setText(breakdown_str)
        else:
            self.format_breakdown.setText("No data available")

        # Load all images into the left pane (image preview list)
        # If you have a QListWidget or similar for thumbnails, update it here
        # For this template, we update the scan_images_list and reset the preview
        self.scan_images_list = image_files.copy()
        self.current_scan_index = 0
        if self.scan_images_list:
            self.show_image_details(self.scan_images_list[0])
        
        # Calculate total size asynchronously to avoid blocking UI
        # Use QTimer to batch process file sizes
        from PyQt5.QtCore import QTimer
        if not hasattr(self, '_size_calc_timer'):
            self._size_calc_timer = QTimer()
            self._size_calc_timer.timeout.connect(self._calculate_folder_size_batch)
            self._size_calc_timer.setSingleShot(False)
            self._size_calc_timer.setInterval(50)  # Process in batches every 50ms
        
        # Reset and start size calculation
        self._pending_size_files = image_files.copy()
        self._calculated_total_size = 0
        self._calculated_count = 0
        if self._pending_size_files:
            self._size_calc_timer.start()
        else:
            # No files, set size to 0 immediately
            self.total_size_label.setText("0 KB")
            self.avg_size_label.setText("0 B")
    
    def _calculate_folder_size_batch(self):
        """Calculate file sizes in batches to avoid blocking UI"""
        if not hasattr(self, '_pending_size_files') or not self._pending_size_files:
            self._size_calc_timer.stop()
            return
        
        # Process up to 10 files per batch
        batch_size = 10
        processed = 0
        
        while self._pending_size_files and processed < batch_size:
            file_path = self._pending_size_files.pop(0)
            try:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    self._calculated_total_size += size
                    self._calculated_count += 1
            except Exception as e:
                # Skip files that can't be read
                pass
            processed += 1
        
        # Update UI with current progress
        if self._calculated_count > 0:
            total_size_kb = self._calculated_total_size // 1024
            avg_size = int(self._calculated_total_size / self._calculated_count)
            avg_size_kb = avg_size // 1024
            
            self.total_size_label.setText(f"{total_size_kb} KB")
            if avg_size_kb > 0:
                self.avg_size_label.setText(f"{avg_size_kb} KB")
            else:
                self.avg_size_label.setText(f"{avg_size} B")
        
        # Stop if all files processed
        if not self._pending_size_files:
            self._size_calc_timer.stop()
            # Final update
            if self._calculated_count > 0:
                total_size_kb = self._calculated_total_size // 1024
                avg_size = int(self._calculated_total_size / self._calculated_count)
                avg_size_kb = avg_size // 1024
                
                self.total_size_label.setText(f"{total_size_kb} KB")
                if avg_size_kb > 0:
                    self.avg_size_label.setText(f"{avg_size_kb} KB")
                else:
                    self.avg_size_label.setText(f"{avg_size} B")
    
    def show_image_details(self, image_path):
        """Display the selected image and its properties in the details tab."""
        self.current_image = image_path
        try:
            pixmap = QPixmap(image_path)
            self.image_preview.setPixmap(pixmap.scaled(
                self.image_preview.width(), self.image_preview.height(), Qt.KeepAspectRatio
            ))
            # Get image size
            size_str = f"{pixmap.width()}x{pixmap.height()} pixels"
            # Get file size
            file_size = os.path.getsize(image_path)
            file_size_str = f"{file_size // 1024} KB"
            # Compose properties text
            props = f"Image: {image_path}\nSize: {size_str}\nFile Size: {file_size_str}"
            self.image_properties.setPlainText(props)
        except Exception as e:
            self.image_preview.setText("Error loading image")
            self.image_properties.setPlainText(f"Error: {str(e)}")
    
    def on_aruco_file_processed(self, result):
        """Handle per-file ArUco processing result (update results table in real time if desired)."""
        filename = result.get('filename', 'Unknown')
        detection_info = result.get('detection_info', {})
        detected_ids = detection_info.get('detected_ids', [])
        midpoints = detection_info.get('marker_midpoints', [])
        # Show all 20 markers
        marker_strs = []
        for marker_id in range(1, 21):
            if marker_id in detected_ids:
                idx = detected_ids.index(marker_id)
                pt = midpoints[idx]
                x, y = (int(round(pt[0])), int(round(pt[1]))) if isinstance(pt, (tuple, list)) and len(pt) == 2 else ("NA", "NA")
                marker_strs.append(f"{marker_id}: {x},{y}")
            else:
                marker_strs.append(f"{marker_id}: NA")
        marker_summary = "; ".join(marker_strs)
        self.aruco_results_text.append(f"Processed: {filename} | Markers: {marker_summary}")

    def on_aruco_processing_finished(self, results):
        """Handle completion of ArUco batch processing."""
        processed_files = results.get('processed_files', [])
        # Force expected markers to [1..20] and check detection
        expected_markers = list(range(1, 21))
        for result in processed_files:
            detection_info = result.get('detection_info', {})
            detected_ids = set(detection_info.get('detected_ids', []))
            missing = [mid for mid in expected_markers if mid not in detected_ids]
            extra = [mid for mid in detected_ids if mid not in expected_markers]
            print(f"[CHECK] {result.get('filename', '')}: Detected={sorted(detected_ids)}, Missing={missing}, Extra={extra}")
        self.populate_aruco_results_table(processed_files)
        self.aruco_progress_bar.setVisible(False)
        self.process_aruco_button.setEnabled(True)
        self.aruco_status_label.setText(results.get('message', 'Processing complete.'))
        self.aruco_results_text.append("\nBatch processing complete.")
    
    def on_pipeline_file_processed(self, result):
        """Handle per-file pipeline processing result"""
        filename = result.get('filename', 'Unknown')
        success = result.get('success', False)
        error_stage = result.get('error_stage', None)
        
        if success:
            stages = result.get('stages', {})
            stage_summary = []
            for stage_name, stage_result in stages.items():
                if stage_result.get('success'):
                    stage_summary.append(f"✅{stage_name}")
                else:
                    stage_summary.append(f"❌{stage_name}")
            
            self.aruco_results_text.append(f"✅ {filename}: {' '.join(stage_summary)}")
            
            # Log roll number if extracted
            roll_number = stages.get('roll_number_extraction', {}).get('roll_number')
            if roll_number:
                self.aruco_results_text.append(f"🆔 {filename}: Roll Number - {roll_number}")
            
            # Log API upload status
            if result.get('api_upload_success'):
                upload_id = stages.get('api_upload', {}).get('upload_id')
                self.aruco_results_text.append(f"📤 {filename}: Uploaded to API - {upload_id}")
        else:
            self.aruco_results_text.append(f"❌ {filename}: Failed at {error_stage}")
    
    def on_pipeline_processing_finished(self, results):
        """Handle completion of pipeline batch processing."""
        # Check for errors first
        error_message = results.get('message', '')
        is_error = error_message and ('error' in error_message.lower() or 'failed' in error_message.lower() or results.get('total', 0) == 0)
        
        # Update processing log dialog
        if hasattr(self, 'processing_log_dialog') and self.processing_log_dialog:
            if is_error:
                # Show error
                self.processing_log_dialog.processing_error(error_message)
            else:
                # Show success with results
                processed_files = results.get('processed_files', [])
                success_count = sum(1 for result in processed_files if result.get('success', False))
                failure_count = len(processed_files) - success_count
                total_files = len(processed_files)
                total_time_all = sum(result.get('total_time_seconds', 0) or 0 for result in processed_files)
                stage_time_totals: Dict[str, float] = {}
                for result in processed_files:
                    for stage_name, elapsed in result.get('stage_times', {}).items():
                        stage_time_totals[stage_name] = stage_time_totals.get(stage_name, 0) + (elapsed or 0)
                
                self.processing_log_dialog.add_log("\n" + "="*80)
                self.processing_log_dialog.add_log("📊 FINAL RESULTS:")
                self.processing_log_dialog.add_log(f"   ✅ Successful: {success_count}")
                self.processing_log_dialog.add_log(f"   ❌ Failed: {failure_count}")
                self.processing_log_dialog.add_log(f"   📊 Total: {total_files}")
                if total_files > 0:
                    success_rate = (success_count / total_files) * 100
                    self.processing_log_dialog.add_log(f"   📈 Success Rate: {success_rate:.1f}%")
                    avg_time = total_time_all / total_files
                    self.processing_log_dialog.add_log(f"   ⏱️ Avg per file: {avg_time:.2f}s")
                self.processing_log_dialog.add_log(f"   ⏱️ Total time (all files): {total_time_all:.2f}s")
                if stage_time_totals:
                    self.processing_log_dialog.add_log("   ⏱️ Time by stage (sum over files):")
                    for stage_name, elapsed in sorted(stage_time_totals.items(), key=lambda x: x[1], reverse=True):
                        self.processing_log_dialog.add_log(f"      • {stage_name}: {elapsed:.2f}s")
                self.processing_log_dialog.add_log("="*80)
                self.processing_log_dialog.processing_complete()
        
        # Update UI
        self.aruco_progress_bar.setVisible(False)
        self.process_pipeline_button.setEnabled(True)
        self.process_aruco_button.setEnabled(True)
        
        if is_error:
            self.aruco_status_label.setText(f"Error: {error_message}")
        else:
            processed_files = results.get('processed_files', [])
            success_count = sum(1 for result in processed_files if result.get('success', False))
            failure_count = len(processed_files) - success_count
            total_time_all = sum(result.get('total_time_seconds', 0) or 0 for result in processed_files)
            stage_time_totals: Dict[str, float] = {}
            for result in processed_files:
                for stage_name, elapsed in result.get('stage_times', {}).items():
                    stage_time_totals[stage_name] = stage_time_totals.get(stage_name, 0) + (elapsed or 0)

            self.aruco_status_label.setText(results.get('message', 'Pipeline processing complete.'))
            self.aruco_results_text.append(f"\n🎉 Pipeline processing complete: {success_count} success, {failure_count} failure")
            self.add_to_processing_log(f"⏱️ Total pipeline time (all files): {total_time_all:.2f}s")
            if processed_files:
                avg_time = total_time_all / len(processed_files)
                self.add_to_processing_log(f"⏱️ Avg per file: {avg_time:.2f}s")
            if stage_time_totals:
                stage_summary = ", ".join([f"{k}: {v:.2f}s" for k, v in sorted(stage_time_totals.items(), key=lambda x: x[1], reverse=True)])
                self.add_to_processing_log(f"⏱️ Stage times (sum over files): {stage_summary}")
        
        # Refresh thumbnail viewers
        self.refresh_thumbnail_viewers()
        
        # Note: Don't show another message box - the popup dialog already shows completion/error

    def create_uploaded_results_tab(self, results_data):
        """Create the uploaded results tab with table display."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Header frame
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #c3e6c3;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title = QLabel("📊 Uploaded Results")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2d5a2d;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        # Summary info
        summary_label = QLabel(f"Total Records: {len(results_data)}")
        summary_label.setFont(QFont("Arial", 12))
        summary_label.setStyleSheet("color: #4a7c59;")
        summary_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(summary_label)
        
        layout.addWidget(header_frame)
        
        # Table widget
        self.uploaded_results_table = QTableWidget()
        self.uploaded_results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3f72af;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
        """)
        
        # Set up table
        self.populate_uploaded_results_table(results_data)
        
        layout.addWidget(self.uploaded_results_table)
        
        return widget

    def populate_uploaded_results_table(self, results_data):
        """Populate the uploaded results table with data."""
        if not results_data:
            return
        
        # Get column headers from first row
        headers = list(results_data[0].keys())
        
        # Set up table dimensions
        self.uploaded_results_table.setRowCount(len(results_data))
        self.uploaded_results_table.setColumnCount(len(headers))
        self.uploaded_results_table.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for row_idx, row_data in enumerate(results_data):
            for col_idx, header in enumerate(headers):
                value = row_data.get(header, '')
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.uploaded_results_table.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns
        self.uploaded_results_table.resizeColumnsToContents()
        
        # Store the data for potential export
        self.uploaded_results_data = results_data

    def add_uploaded_results_tab(self, results_data):
        """Add or update the uploaded results tab."""
        # Remove existing tab if it exists
        if self.uploaded_results_tab_index is not None:
            self.tab_widget.removeTab(self.uploaded_results_tab_index)
        
        # Create new tab
        self.uploaded_results_tab = self.create_uploaded_results_tab(results_data)
        self.uploaded_results_tab_index = self.tab_widget.addTab(
            self.uploaded_results_tab, 
            "📊 Uploaded Results"
        )

    def show_uploaded_results_tab(self):
        """Switch to the uploaded results tab."""
        if self.uploaded_results_tab_index is not None:
            self.tab_widget.setCurrentIndex(self.uploaded_results_tab_index)
    
    def refresh_thumbnail_viewers(self):
        """Refresh thumbnails in success and error folders"""
        if not self.current_folder:
            print(f"[ResultsPanel] refresh_thumbnail_viewers: No current folder set")
            return
        
        success_folder = os.path.join(self.current_folder, "success")
        error_folder = os.path.join(self.current_folder, "error")
        
        print(f"[ResultsPanel] refresh_thumbnail_viewers called")
        print(f"[ResultsPanel]   Current folder: {self.current_folder}")
        print(f"[ResultsPanel]   Success folder: {success_folder}")
        print(f"[ResultsPanel]   Error folder: {error_folder}")
        print(f"[ResultsPanel]   Success exists: {os.path.exists(success_folder)}")
        print(f"[ResultsPanel]   Error exists: {os.path.exists(error_folder)}")
        
        # Load success thumbnails
        if os.path.exists(success_folder):
            try:
                self.success_thumbnail_viewer.load_thumbnails(success_folder)
                print(f"[ResultsPanel] Loaded {len(self.success_thumbnail_viewer.thumbnails)} success thumbnails")
            except Exception as e:
                print(f"[ResultsPanel] Error loading success thumbnails: {e}")
        else:
            print(f"[ResultsPanel] Success folder does not exist")
        
        # Load error thumbnails
        if os.path.exists(error_folder):
            try:
                self.error_thumbnail_viewer.load_thumbnails(error_folder)
                print(f"[ResultsPanel] Loaded {len(self.error_thumbnail_viewer.thumbnails)} error thumbnails")
            except Exception as e:
                print(f"[ResultsPanel] Error loading error thumbnails: {e}")
        else:
            print(f"[ResultsPanel] Error folder does not exist")
    
    def clear_thumbnail_viewers(self):
        """Clear all thumbnails (called when folder changes)"""
        self.success_thumbnail_viewer.clear_thumbnails()
        self.error_thumbnail_viewer.clear_thumbnails()
        print(f"[ResultsPanel] Cleared thumbnail viewers")
    
    def show_image_popup(self, image_path):
        """Show image in popup dialog with rerun option"""
        from .thumbnail_viewer import ImagePopupDialog
        
        popup = ImagePopupDialog(image_path, self)
        popup.rerun_requested.connect(self.handle_rerun_request)
        popup.exec_()
    
    def handle_rerun_request(self, image_path):
        """Handle rerun request for a specific image"""
        # Extract original image path from success/error path
        # The filename might be roll_number.png in success/error folder
        # Need to find the original image in the main folder
        
        filename = os.path.basename(image_path)
        
        # Check if this is a roll number filename or original filename
        # For now, show message that rerun is requested
        QMessageBox.information(
            self,
            "Rerun Pipeline",
            f"Rerun requested for: {filename}\n\n"
            "To rerun a specific file:\n"
            "1. Locate the original image in the main folder\n"
            "2. Select it from the image list\n"
            "3. Run pipeline processing\n\n"
            "Note: Automatic single-file rerun will be added in future version."
        )
