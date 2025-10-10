#!/usr/bin/env python3
"""
Horizontal Thumbnail Viewer for Success and Error Images
"""

import os
import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QPushButton, QDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize


class ImagePopupDialog(QDialog):
    """Popup dialog to show full image with rerun option"""
    
    rerun_requested = pyqtSignal(str)  # Signal to request pipeline rerun
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle(f"Image: {os.path.basename(image_path)}")
        self.setGeometry(100, 100, 1200, 900)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Top info bar
        info_bar = QHBoxLayout()
        
        filename_label = QLabel(f"📄 {os.path.basename(self.image_path)}")
        filename_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        info_bar.addWidget(filename_label)
        
        info_bar.addStretch()
        
        # Rerun button
        rerun_btn = QPushButton("🔄 Rerun Pipeline for This File")
        rerun_btn.clicked.connect(self.request_rerun)
        rerun_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        info_bar.addWidget(rerun_btn)
        
        close_btn = QPushButton("✖ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        info_bar.addWidget(close_btn)
        
        layout.addLayout(info_bar)
        
        # Scroll area for image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Load and display image
        if os.path.exists(self.image_path):
            img = cv2.imread(self.image_path)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Don't scale, show original size for clarity
                height, width, channel = img_rgb.shape
                bytes_per_line = 3 * width
                q_image = QImage(img_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap)
        
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
    
    def request_rerun(self):
        """Request pipeline rerun for this file"""
        reply = QMessageBox.question(
            self,
            'Rerun Pipeline',
            f'Rerun the pipeline for this image?\n\n{os.path.basename(self.image_path)}\n\n'
            'The image will be reprocessed through all pipeline stages.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Get original image path (remove success/error folder part)
            # The filename is roll_number.png, need to find original
            # For now, emit signal with this path
            self.rerun_requested.emit(self.image_path)
            QMessageBox.information(self, "Rerun Requested", 
                                  "Pipeline rerun has been requested.\n"
                                  "Check the main window for processing status.")
            self.close()


class ThumbnailViewer(QWidget):
    """Horizontal scrollable thumbnail viewer"""
    
    thumbnail_clicked = pyqtSignal(str)  # Signal when thumbnail is clicked
    
    def __init__(self, title, color="#4CAF50"):
        super().__init__()
        self.title = title
        self.color = color
        self.thumbnails = []
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Set minimum size for the widget
        self.setMinimumHeight(200)
        self.setMaximumHeight(200)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
            background-color: {self.color};
            color: white;
            border-radius: 3px;
        """)
        layout.addWidget(title_label)
        
        # Scroll area (store as instance variable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Important: False so container can be wider
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setMinimumHeight(180)
        self.scroll_area.setMaximumHeight(180)
        self.scroll_area.setStyleSheet("QScrollArea { border: 2px solid #ccc; background-color: #f9f9f9; }")
        
        # Container for thumbnails
        self.thumbnail_container = QWidget()
        self.thumbnail_container.setMinimumHeight(170)
        self.thumbnail_layout = QHBoxLayout()
        self.thumbnail_layout.setSpacing(10)
        self.thumbnail_layout.setContentsMargins(5, 5, 5, 5)
        self.thumbnail_layout.addStretch()
        self.thumbnail_container.setLayout(self.thumbnail_layout)
        
        self.scroll_area.setWidget(self.thumbnail_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
    
    def clear_thumbnails(self):
        """Clear all thumbnails"""
        # Remove all widgets from layout
        while self.thumbnail_layout.count() > 1:  # Keep the stretch
            item = self.thumbnail_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.thumbnails = []
    
    def load_thumbnails(self, folder_path):
        """Load thumbnails from a folder"""
        print(f"[ThumbnailViewer] load_thumbnails called for: {folder_path}")
        
        if not os.path.exists(folder_path):
            print(f"[ThumbnailViewer] Folder does not exist: {folder_path}")
            return
        
        # Clear existing
        self.clear_thumbnails()
        
        # Get all image files
        image_files = []
        try:
            files_in_folder = os.listdir(folder_path)
            print(f"[ThumbnailViewer] Files in folder: {len(files_in_folder)}")
            
            for file in files_in_folder:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(os.path.join(folder_path, file))
            
            print(f"[ThumbnailViewer] Image files found: {len(image_files)}")
            if image_files:
                print(f"[ThumbnailViewer] Sample files: {[os.path.basename(f) for f in image_files[:3]]}")
        except Exception as e:
            print(f"[ThumbnailViewer] Error listing folder: {e}")
            return
        
        # Sort by filename
        image_files.sort()
        
        # Add thumbnails
        for img_path in image_files:
            try:
                self.add_thumbnail(img_path)
            except Exception as e:
                print(f"[ThumbnailViewer] Error adding thumbnail {os.path.basename(img_path)}: {e}")
        
        # Calculate and set container width based on thumbnails
        # Each thumbnail: 130px width (120 + 10 spacing)
        if len(self.thumbnails) > 0:
            container_width = len(self.thumbnails) * 130 + 50  # Extra padding
            self.thumbnail_container.setMinimumWidth(container_width)
            self.thumbnail_container.setFixedHeight(170)
            print(f"[ThumbnailViewer] Set container width to: {container_width}px for {len(self.thumbnails)} thumbnails")
        else:
            # No thumbnails - set small width
            self.thumbnail_container.setMinimumWidth(200)
            self.thumbnail_container.setFixedHeight(170)
        
        # Force layout and widget updates
        self.thumbnail_layout.update()
        self.thumbnail_container.updateGeometry()
        self.thumbnail_container.adjustSize()
        self.thumbnail_container.update()
        
        # Update scroll area
        self.scroll_area.updateGeometry()
        self.scroll_area.update()
        
        # Update self
        self.updateGeometry()
        self.update()
        
        print(f"[ThumbnailViewer] Finished loading {len(self.thumbnails)} thumbnails")
        print(f"[ThumbnailViewer] Thumbnail container size: {self.thumbnail_container.size()}")
        print(f"[ThumbnailViewer] Scroll area viewport size: {self.scroll_area.viewport().size()}")
        print(f"[ThumbnailViewer] Layout count: {self.thumbnail_layout.count()}")
    
    def add_thumbnail(self, image_path):
        """Add a single thumbnail"""
        print(f"[ThumbnailViewer] add_thumbnail called for: {os.path.basename(image_path)}")
        
        if not os.path.exists(image_path):
            print(f"[ThumbnailViewer] File does not exist: {image_path}")
            return
        
        # Create thumbnail widget
        thumb_widget = QWidget()
        thumb_layout = QVBoxLayout()
        thumb_layout.setContentsMargins(5, 5, 5, 5)
        
        # Image button
        img_btn = QPushButton()
        img_btn.setFixedSize(120, 120)
        img_btn.clicked.connect(lambda: self.thumbnail_clicked.emit(image_path))
        img_btn.setStyleSheet("""
            QPushButton {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 2px;
            }
            QPushButton:hover {
                border: 2px solid #4CAF50;
            }
        """)
        
        # Load and scale image
        img = cv2.imread(image_path)
        if img is not None:
            # Scale to thumbnail size
            height, width = img.shape[:2]
            scale = min(116 / width, 116 / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            img_resized = cv2.resize(img, (new_width, new_height))
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            
            h, w, ch = img_rgb.shape
            bytes_per_line = 3 * w
            q_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Convert QPixmap to QIcon
            icon = QIcon(pixmap)
            img_btn.setIcon(icon)
            img_btn.setIconSize(QSize(new_width, new_height))
        
        thumb_layout.addWidget(img_btn)
        
        # Filename label
        filename = os.path.basename(image_path)
        # Truncate if too long
        if len(filename) > 15:
            display_name = filename[:12] + "..."
        else:
            display_name = filename
        
        name_label = QLabel(display_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 10px;")
        name_label.setToolTip(filename)  # Full name on hover
        thumb_layout.addWidget(name_label)
        
        thumb_widget.setLayout(thumb_layout)
        
        # Insert before the stretch
        insert_position = self.thumbnail_layout.count() - 1
        self.thumbnail_layout.insertWidget(insert_position, thumb_widget)
        self.thumbnails.append(image_path)
        print(f"[ThumbnailViewer] Added thumbnail at position {insert_position}: {display_name}")

