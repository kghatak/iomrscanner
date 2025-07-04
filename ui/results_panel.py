import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QGridLayout, QTextEdit, QTabWidget, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QFont
from PIL import Image
from PIL.ExifTags import TAGS


class ResultsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.current_folder = None
        self.current_image = None
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.next_scan_image)
        self.current_scan_index = 0
        self.scan_images_list = []
        self.is_scanning = False
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
        
        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.upload_button)
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
        
        # Folder Overview Tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📁 Folder Overview")
        
        # Image Details Tab
        self.details_tab = self.create_details_tab()
        self.tab_widget.addTab(self.details_tab, "🖼️ Image Details")
        
        # Add widgets to main layout
        layout.addWidget(header_frame)
        layout.addWidget(self.tab_widget)
        
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
        
    @pyqtSlot(str)
    def analyze_folder(self, folder_path):
        self.current_folder = folder_path
        self.update_folder_overview()
        
    def update_folder_overview(self):
        if not self.current_folder:
            return
            
        try:
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
            files = os.listdir(self.current_folder)
            image_files = [
                f for f in files 
                if os.path.splitext(f.lower())[1] in image_extensions
            ]
            
            if not image_files:
                self.total_images_label.setText("0")
                self.total_size_label.setText("0 B")
                self.avg_size_label.setText("0 B")
                self.formats_label.setText("None")
                self.format_breakdown.setText("No images found in folder")
                return
            
            # Calculate statistics
            total_images = len(image_files)
            total_size = 0
            format_counts = {}
            
            for filename in image_files:
                filepath = os.path.join(self.current_folder, filename)
                try:
                    size = os.path.getsize(filepath)
                    total_size += size
                    
                    ext = os.path.splitext(filename.lower())[1]
                    format_counts[ext] = format_counts.get(ext, 0) + 1
                except:
                    continue
            
            avg_size = total_size / total_images if total_images > 0 else 0
            
            # Update labels
            self.total_images_label.setText(str(total_images))
            self.total_size_label.setText(self.format_file_size(total_size))
            self.avg_size_label.setText(self.format_file_size(avg_size))
            
            formats = list(format_counts.keys())
            self.formats_label.setText(", ".join(formats) if formats else "None")
            
            # Format breakdown
            breakdown_text = ""
            for ext, count in sorted(format_counts.items()):
                percentage = (count / total_images) * 100
                breakdown_text += f"{ext.upper()}: {count} files ({percentage:.1f}%)\n"
            
            self.format_breakdown.setText(breakdown_text.strip())
            
        except Exception as e:
            self.total_images_label.setText("Error")
            self.total_size_label.setText("Error")
            self.avg_size_label.setText("Error")
            self.formats_label.setText("Error")
            self.format_breakdown.setText(f"Error analyzing folder: {str(e)}")
            
    @pyqtSlot(str)
    def show_image_details(self, image_path):
        self.current_image = image_path
        self.update_image_preview(image_path)
        self.update_image_properties(image_path)
        
        # Switch to details tab
        self.tab_widget.setCurrentIndex(1)
        
    def update_image_preview(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale to fit the larger preview area while maintaining aspect ratio
                # Get the scroll area size for better scaling
                available_width = 600  # Approximate available width
                available_height = 400  # Minimum height we set
                
                scaled_pixmap = pixmap.scaled(
                    available_width, available_height, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                
                # If scanning, show filename in window title or status
                if self.is_scanning:
                    filename = os.path.basename(image_path)
                    self.image_preview.setToolTip(f"Currently viewing: {filename}")
            else:
                self.image_preview.setText("Failed to load image")
        except Exception as e:
            self.image_preview.setText(f"Error loading image: {str(e)}")
            
    def update_image_properties(self, image_path):
        try:
            # Basic file properties
            filename = os.path.basename(image_path)
            file_size = os.path.getsize(image_path)
            
            properties = f"File: {filename}\n"
            properties += f"Size: {self.format_file_size(file_size)}\n"
            properties += f"Path: {image_path}\n\n"
            
            # Image properties using PIL
            try:
                with Image.open(image_path) as img:
                    properties += f"Dimensions: {img.width} x {img.height} pixels\n"
                    properties += f"Format: {img.format}\n"
                    properties += f"Mode: {img.mode}\n"
                    
                    # EXIF data
                    if hasattr(img, '_getexif') and img._getexif():
                        properties += "\nEXIF Data:\n"
                        exif = img._getexif()
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if isinstance(value, str) and len(str(value)) < 100:
                                properties += f"  {tag}: {value}\n"
                    else:
                        properties += "\nNo EXIF data available\n"
                        
            except Exception as e:
                properties += f"\nError reading image properties: {str(e)}\n"
                
            self.image_properties.setPlainText(properties)
            
        except Exception as e:
            self.image_properties.setPlainText(f"Error: {str(e)}")
            
    def format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def start_scan_all_images(self):
        """Start scanning all images in the current folder"""
        if not self.current_folder:
            return
            
        # Get all image files
        try:
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
            files = os.listdir(self.current_folder)
            self.scan_images_list = [
                os.path.join(self.current_folder, f) for f in files 
                if os.path.splitext(f.lower())[1] in image_extensions
            ]
            
            if not self.scan_images_list:
                return
                
            # Switch to details tab and start scanning
            self.tab_widget.setCurrentIndex(1)
            self.current_scan_index = 0
            self.is_scanning = True
            
            # Update button text and disable it
            self.scan_button.setText("🔄 Processing...")
            self.scan_button.setEnabled(False)
            
            # Start the timer (20 seconds per image)
            self.scan_timer.start(2000)  # 2 seconds = 2000 milliseconds
            
            # Load first image immediately
            self.load_scan_image()
            
        except Exception as e:
            print(f"Error starting scan: {e}")
    
    def load_scan_image(self):
        """Load the current scan image"""
        if self.current_scan_index < len(self.scan_images_list):
            image_path = self.scan_images_list[self.current_scan_index]
            self.update_image_preview(image_path)
            self.update_image_properties(image_path)
            
            # Update scan button to show progress
            progress = f"Processing... ({self.current_scan_index + 1}/{len(self.scan_images_list)})"
            self.scan_button.setText(progress)
    
    def next_scan_image(self):
        """Move to the next image in scan"""
        self.current_scan_index += 1
        
        if self.current_scan_index < len(self.scan_images_list):
            # Load next image
            self.load_scan_image()
        else:
            # Scanning complete
            self.stop_scanning()
    
    def stop_scanning(self):
        """Stop the scanning process"""
        self.scan_timer.stop()
        self.is_scanning = False
        self.scan_button.setText("🔍 Scan All Images")
        self.scan_button.setEnabled(True)
        
        # Show completion message
        self.image_preview.setText("✅ Scan completed!\nAll images have been processed.")
    
    def upload_results(self):
        """Handle upload results functionality"""
        from PyQt5.QtWidgets import QMessageBox, QFileDialog
        
        if not self.current_folder:
            QMessageBox.warning(self, "No Data", "No folder analyzed yet. Please select a folder first.")
            return
        
        # Get save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Analysis Results",
            f"image_analysis_results.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                # Collect analysis data
                total_images = self.total_images_label.text()
                total_size = self.total_size_label.text()
                avg_size = self.avg_size_label.text()
                formats = self.formats_label.text()
                breakdown = self.format_breakdown.text()
                
                # Create report
                report = f"""Image Folder Analysis Report
Generated on: {self.current_folder}

SUMMARY:
========
Total Images: {total_images}
Total Size: {total_size}
Average Size: {avg_size}
Formats Found: {formats}

FORMAT BREAKDOWN:
================
{breakdown}

Generated by Image Folder Analyzer v1.0
"""
                
                # Save to file
                with open(filename, 'w') as f:
                    f.write(report)
                
                QMessageBox.information(self, "Success", f"Results saved to:\n{filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save results:\n{str(e)}")
