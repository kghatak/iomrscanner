import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QScrollArea, QFrame
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
