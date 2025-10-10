#!/usr/bin/env python3
"""
Manual Review Tool for OMR Circle Dataset - Tabbed View

Fast review interface with:
- Three tabs for different confidence levels
- Sorted by confidence within each tab
- Green highlighting for changed labels
- Bulk approve functionality
"""

import sys
import os
import pandas as pd
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QMessageBox, QTabWidget)
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import Qt


class CircleReviewTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OMR Circle Review Tool - Confidence-Based Tabs")
        self.setGeometry(50, 50, 1600, 900)
        
        self.dataset_dir = None
        self.metadata_df = None
        self.patches_dir = None
        self.last_folder_file = os.path.expanduser("~/.omr_review_last_folder.txt")
        
        # DataFrames for each tab
        self.df_low = None  # <50%
        self.df_medium = None  # 50-90%
        self.df_high = None  # >90%
        
        self.init_ui()
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Top controls
        top_layout = QHBoxLayout()
        
        load_btn = QPushButton("📁 Load Dataset Directory")
        load_btn.clicked.connect(self.load_dataset)
        load_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        top_layout.addWidget(load_btn)
        
        self.save_btn = QPushButton("💾 Save All Changes")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("font-size: 14px; padding: 8px; background-color: #90EE90;")
        top_layout.addWidget(self.save_btn)
        
        self.bulk_approve_btn = QPushButton("✅ Bulk Approve All Tabs")
        self.bulk_approve_btn.clicked.connect(self.bulk_approve_all)
        self.bulk_approve_btn.setEnabled(False)
        self.bulk_approve_btn.setStyleSheet("font-size: 14px; padding: 8px; background-color: #87CEEB;")
        top_layout.addWidget(self.bulk_approve_btn)
        
        top_layout.addStretch()
        
        main_layout.addLayout(top_layout)
        
        # Info label
        self.info_label = QLabel("Load a dataset to begin review")
        self.info_label.setStyleSheet("font-size: 14px; padding: 10px; font-weight: bold;")
        main_layout.addWidget(self.info_label)
        
        # Stats label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 12px; padding: 8px; background-color: #f0f0f0;")
        main_layout.addWidget(self.stats_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create three tabs
        self.table_low = self.create_table()
        self.table_medium = self.create_table()
        self.table_high = self.create_table()
        
        self.tab_widget.addTab(self.table_low, "🔴 Low Confidence (<50%)")
        self.tab_widget.addTab(self.table_medium, "🟡 Medium Confidence (50-90%)")
        self.tab_widget.addTab(self.table_high, "🟢 High Confidence (>90%)")
        
        main_layout.addWidget(self.tab_widget)
        
        # Instructions
        instructions = QLabel(
            "💡 Instructions: Review patches sorted by confidence. "
            "Click 'Mark' or 'Unmark' to set labels. "
            "Changed labels (different from initial) are highlighted in GREEN. "
            "Use 'Bulk Approve All' to accept all initial labels at once."
        )
        instructions.setStyleSheet("padding: 10px; background-color: #e8f4f8;")
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
    
    def create_table(self):
        """Create a table widget with standard configuration"""
        table = QTableWidget()
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            'Patch', 'Col', 'Q', 'Opt', 'Confidence', 'Fill Ratio',
            'Initial Label', 'Reviewed Label', 'Action', 'Preview'
        ])
        
        # Table properties
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        # Column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Stretch)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        table.setColumnWidth(9, 100)
        
        # Row height
        table.verticalHeader().setDefaultSectionSize(80)
        
        return table
    
    def load_dataset(self):
        # Try to get last used folder
        start_dir = ""
        if os.path.exists(self.last_folder_file):
            try:
                with open(self.last_folder_file, 'r') as f:
                    start_dir = f.read().strip()
                    if not os.path.exists(start_dir):
                        start_dir = ""
            except:
                pass
        
        dataset_dir = QFileDialog.getExistingDirectory(
            self, "Select Dataset Directory", start_dir
        )
        
        if not dataset_dir:
            return
        
        # Save the selected folder for next time
        try:
            with open(self.last_folder_file, 'w') as f:
                f.write(dataset_dir)
        except:
            pass  # Silently fail if can't save
        
        metadata_path = os.path.join(dataset_dir, "metadata.csv")
        
        if not os.path.exists(metadata_path):
            QMessageBox.critical(self, "Error", "metadata.csv not found in selected directory")
            return
        
        self.dataset_dir = dataset_dir
        self.patches_dir = os.path.join(dataset_dir, "patches")
        
        try:
            self.metadata_df = pd.read_csv(metadata_path)
            
            # Ensure reviewed_label column exists
            if 'reviewed_label' not in self.metadata_df.columns:
                self.metadata_df['reviewed_label'] = ''
            
            # Split into three DataFrames based on confidence
            self.df_low = self.metadata_df[self.metadata_df['confidence'] < 0.5].copy()
            self.df_medium = self.metadata_df[
                (self.metadata_df['confidence'] >= 0.5) & 
                (self.metadata_df['confidence'] <= 0.9)
            ].copy()
            self.df_high = self.metadata_df[self.metadata_df['confidence'] > 0.9].copy()
            
            # Sort each by confidence (low to high within each tab)
            self.df_low = self.df_low.sort_values('confidence', ascending=True).reset_index(drop=True)
            self.df_medium = self.df_medium.sort_values('confidence', ascending=True).reset_index(drop=True)
            self.df_high = self.df_high.sort_values('confidence', ascending=True).reset_index(drop=True)
            
            # Populate tables
            self.populate_table_with_data(self.table_low, self.df_low)
            self.populate_table_with_data(self.table_medium, self.df_medium)
            self.populate_table_with_data(self.table_high, self.df_high)
            
            # Update tab labels with counts
            self.tab_widget.setTabText(0, f"🔴 Low Confidence (<50%) - {len(self.df_low)} patches")
            self.tab_widget.setTabText(1, f"🟡 Medium Confidence (50-90%) - {len(self.df_medium)} patches")
            self.tab_widget.setTabText(2, f"🟢 High Confidence (>90%) - {len(self.df_high)} patches")
            
            self.update_stats()
            
            self.save_btn.setEnabled(True)
            self.bulk_approve_btn.setEnabled(True)
            
            QMessageBox.information(
                self, "Success", 
                f"Loaded {len(self.metadata_df)} patches\n\n"
                f"🔴 Low (<50%): {len(self.df_low)} patches\n"
                f"🟡 Medium (50-90%): {len(self.df_medium)} patches\n"
                f"🟢 High (>90%): {len(self.df_high)} patches\n\n"
                f"Review low confidence patches first!"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dataset: {str(e)}")
    
    def populate_table_with_data(self, table, df):
        """Populate a table with data from a DataFrame"""
        if df is None or len(df) == 0:
            table.setRowCount(0)
            return
        
        table.setRowCount(len(df))
        
        for table_row_idx, (df_idx, row) in enumerate(df.iterrows()):
            # Store original DataFrame index in table item for later lookup
            # Column 0: Patch name
            patch_item = QTableWidgetItem(row['image_name'])
            patch_item.setData(Qt.UserRole, df_idx)  # Store original index
            table.setItem(table_row_idx, 0, patch_item)
            
            # Column 1: Column number
            table.setItem(table_row_idx, 1, QTableWidgetItem(str(row['column'])))
            
            # Column 2: Question number
            table.setItem(table_row_idx, 2, QTableWidgetItem(str(row['question'])))
            
            # Column 3: Option
            table.setItem(table_row_idx, 3, QTableWidgetItem(row['option']))
            
            # Column 4: Confidence
            conf_item = QTableWidgetItem(f"{row['confidence']:.3f}")
            table.setItem(table_row_idx, 4, conf_item)
            
            # Column 5: Fill Ratio
            fill_item = QTableWidgetItem(f"{row['fill_ratio']:.3f}")
            # Color code by fill ratio
            if row['fill_ratio'] > 0.4:
                fill_item.setBackground(QColor(200, 255, 200))  # Green
            elif row['fill_ratio'] < 0.2:
                fill_item.setBackground(QColor(240, 240, 240))  # Gray
            else:
                fill_item.setBackground(QColor(255, 255, 200))  # Yellow
            table.setItem(table_row_idx, 5, fill_item)
            
            # Column 6: Initial Label
            initial_item = QTableWidgetItem(row['initial_label'])
            # Background: gray for marked, white for unmarked
            if row['initial_label'] == 'marked':
                initial_item.setBackground(QColor(200, 200, 200))  # Gray background
                initial_item.setForeground(QColor(0, 0, 0))  # Black text
            else:
                initial_item.setBackground(QColor(255, 255, 255))  # White background
                initial_item.setForeground(QColor(0, 0, 0))  # Black text
            table.setItem(table_row_idx, 6, initial_item)
            
            # Column 7: Reviewed Label
            reviewed_label = row.get('reviewed_label', '')
            if pd.isna(reviewed_label):
                reviewed_label = ''
            
            reviewed_item = QTableWidgetItem(reviewed_label if reviewed_label else '(pending)')
            
            # Check if label was changed from initial
            if reviewed_label and reviewed_label != row['initial_label']:
                # CHANGED from initial → GREEN BACKGROUND
                reviewed_item.setBackground(QColor(144, 238, 144))  # Light green
                reviewed_item.setForeground(QColor(0, 0, 0))  # Black text
            elif reviewed_label == 'marked':
                reviewed_item.setForeground(QColor(0, 128, 0))  # Dark green text
            elif reviewed_label == 'unmarked':
                reviewed_item.setForeground(QColor(100, 100, 100))  # Gray text
            
            table.setItem(table_row_idx, 7, reviewed_item)
            
            # Column 8: Action buttons
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(2, 2, 2, 2)
            
            mark_btn = QPushButton("Mark")
            mark_btn.clicked.connect(lambda checked, tidx=table_row_idx, didx=df_idx: 
                                    self.set_label(tidx, didx, 'marked'))
            mark_btn.setStyleSheet("background-color: #90EE90; padding: 4px; font-weight: bold;")
            
            unmark_btn = QPushButton("Unmark")
            unmark_btn.clicked.connect(lambda checked, tidx=table_row_idx, didx=df_idx: 
                                      self.set_label(tidx, didx, 'unmarked'))
            unmark_btn.setStyleSheet("background-color: #D3D3D3; padding: 4px;")
            
            button_layout.addWidget(mark_btn)
            button_layout.addWidget(unmark_btn)
            button_widget.setLayout(button_layout)
            
            table.setCellWidget(table_row_idx, 8, button_widget)
            
            # Column 9: Preview image
            patch_path = os.path.join(self.patches_dir, row['image_name'])
            if os.path.exists(patch_path):
                img = cv2.imread(patch_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Scale up for visibility
                scale = 3
                img_scaled = cv2.resize(img, None, fx=scale, fy=scale, 
                                       interpolation=cv2.INTER_NEAREST)
                
                height, width, channel = img_scaled.shape
                bytes_per_line = 3 * width
                q_image = QImage(img_scaled.data, width, height, 
                                bytes_per_line, QImage.Format_RGB888)
                
                pixmap = QPixmap.fromImage(q_image)
                
                img_label = QLabel()
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                
                table.setCellWidget(table_row_idx, 9, img_label)
    
    def set_label(self, table_row_idx: int, df_idx: int, label: str):
        """Set the reviewed label for a specific row"""
        if self.metadata_df is None:
            return
        
        # Get the current table
        current_table = self.tab_widget.currentWidget()
        
        # Update main dataframe
        self.metadata_df.at[df_idx, 'reviewed_label'] = label
        
        # Update table cell
        reviewed_item = current_table.item(table_row_idx, 7)
        reviewed_item.setText(label)
        
        # Get initial label to check if changed
        initial_label = self.metadata_df.at[df_idx, 'initial_label']
        
        # If label is DIFFERENT from initial → GREEN BACKGROUND
        if label != initial_label:
            reviewed_item.setBackground(QColor(144, 238, 144))  # Light green
            reviewed_item.setForeground(QColor(0, 0, 0))  # Black text
        else:
            # Same as initial → Normal colors
            reviewed_item.setBackground(QColor(255, 255, 255))  # White
            if label == 'marked':
                reviewed_item.setForeground(QColor(0, 128, 0))  # Dark green text
            elif label == 'unmarked':
                reviewed_item.setForeground(QColor(100, 100, 100))  # Gray text
        
        self.update_stats()
    
    def bulk_approve_all(self):
        """Bulk approve all initial labels across all tabs (only for empty reviewed_label)"""
        if self.metadata_df is None:
            return
        
        # Count how many will be filled
        empty_mask = (self.metadata_df['reviewed_label'].isna()) | (self.metadata_df['reviewed_label'] == '')
        num_to_fill = empty_mask.sum()
        num_already_reviewed = len(self.metadata_df) - num_to_fill
        
        reply = QMessageBox.question(
            self,
            'Bulk Approve All Tabs',
            f'Copy initial labels to reviewed labels for EMPTY cells only?\n\n'
            f'📊 Total patches: {len(self.metadata_df)}\n'
            f'✅ Already reviewed: {num_already_reviewed} (will NOT be changed)\n'
            f'⏳ Pending (empty): {num_to_fill} (will be filled)\n\n'
            f'Breakdown by confidence:\n'
            f'🔴 Low: {len(self.df_low)} patches\n'
            f'🟡 Medium: {len(self.df_medium)} patches\n'
            f'🟢 High: {len(self.df_high)} patches\n\n'
            f'Your manual reviews will be preserved!',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Copy initial_label to reviewed_label ONLY for empty cells
            for idx in self.metadata_df.index:
                reviewed = self.metadata_df.at[idx, 'reviewed_label']
                if pd.isna(reviewed) or reviewed == '':
                    self.metadata_df.at[idx, 'reviewed_label'] = self.metadata_df.at[idx, 'initial_label']
            
            # Update all three tables
            self.update_all_tables()
            
            self.update_stats()
            QMessageBox.information(self, "Success", 
                                  f"✅ Bulk approved {num_to_fill} empty patches!\n"
                                  f"✅ Preserved {num_already_reviewed} manual reviews!")
    
    def update_all_tables(self):
        """Refresh all three tables after bulk operations"""
        # Update DataFrames from main df
        for idx, row in self.metadata_df.iterrows():
            # Update the split DataFrames
            conf = row['confidence']
            if conf < 0.5:
                df_to_update = self.df_low
            elif conf <= 0.9:
                df_to_update = self.df_medium
            else:
                df_to_update = self.df_high
            
            # Find and update in the appropriate df
            mask = (df_to_update.index == idx)
            if mask.any():
                df_to_update.loc[idx, 'reviewed_label'] = row['reviewed_label']
        
        # Repopulate all tables
        self.populate_table_with_data(self.table_low, self.df_low)
        self.populate_table_with_data(self.table_medium, self.df_medium)
        self.populate_table_with_data(self.table_high, self.df_high)
    
    def save_changes(self):
        """Save all changes to metadata.csv"""
        if self.metadata_df is None:
            return
        
        metadata_path = os.path.join(self.dataset_dir, "metadata.csv")
        
        try:
            # Save the main dataframe (has all changes)
            self.metadata_df.to_csv(metadata_path, index=False)
            
            # Count changes
            total = len(self.metadata_df)
            reviewed = (self.metadata_df['reviewed_label'] != '').sum()
            changed = (
                (self.metadata_df['reviewed_label'] != '') & 
                (self.metadata_df['reviewed_label'] != self.metadata_df['initial_label'])
            ).sum()
            
            QMessageBox.information(
                self, "Saved", 
                f"💾 All changes saved to:\n{metadata_path}\n\n"
                f"Total: {total}\n"
                f"Reviewed: {reviewed}\n"
                f"Changed from initial: {changed}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def update_stats(self):
        """Update statistics display"""
        if self.metadata_df is None:
            return
        
        # Count reviewed labels
        reviewed = self.metadata_df['reviewed_label'].notna() & (self.metadata_df['reviewed_label'] != '')
        reviewed_count = reviewed.sum()
        total = len(self.metadata_df)
        
        # Count by label in reviewed
        marked_count = (self.metadata_df['reviewed_label'] == 'marked').sum()
        unmarked_count = (self.metadata_df['reviewed_label'] == 'unmarked').sum()
        pending_count = total - reviewed_count
        
        # Count changes (different from initial)
        changed_count = (
            (self.metadata_df['reviewed_label'] != '') & 
            (self.metadata_df['reviewed_label'] != self.metadata_df['initial_label'])
        ).sum()
        
        # Tab counts
        low_count = len(self.df_low)
        med_count = len(self.df_medium)
        high_count = len(self.df_high)
        
        stats_text = (
            f"📊 Total: {total} | "
            f"✅ Reviewed: {reviewed_count} ({reviewed_count/total*100:.1f}%) | "
            f"⏳ Pending: {pending_count} | "
            f"🔄 Changed: {changed_count} | "
            f"🟢 Marked: {marked_count} | "
            f"⚪ Unmarked: {unmarked_count} || "
            f"Tabs: 🔴 {low_count} | 🟡 {med_count} | 🟢 {high_count}"
        )
        self.stats_label.setText(stats_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = CircleReviewTool()
    window.show()
    
    # Try to auto-load last used folder
    if os.path.exists(window.last_folder_file):
        try:
            with open(window.last_folder_file, 'r') as f:
                last_folder = f.read().strip()
                if os.path.exists(last_folder):
                    metadata_path = os.path.join(last_folder, "metadata.csv")
                    if os.path.exists(metadata_path):
                        # Auto-load the last folder
                        window.dataset_dir = last_folder
                        window.patches_dir = os.path.join(last_folder, "patches")
                        window.metadata_df = pd.read_csv(metadata_path)
                        
                        # Ensure reviewed_label column exists
                        if 'reviewed_label' not in window.metadata_df.columns:
                            window.metadata_df['reviewed_label'] = ''
                        
                        # Split and populate
                        window.df_low = window.metadata_df[window.metadata_df['confidence'] < 0.5].copy()
                        window.df_medium = window.metadata_df[
                            (window.metadata_df['confidence'] >= 0.5) & 
                            (window.metadata_df['confidence'] <= 0.9)
                        ].copy()
                        window.df_high = window.metadata_df[window.metadata_df['confidence'] > 0.9].copy()
                        
                        window.df_low = window.df_low.sort_values('confidence', ascending=True).reset_index(drop=True)
                        window.df_medium = window.df_medium.sort_values('confidence', ascending=True).reset_index(drop=True)
                        window.df_high = window.df_high.sort_values('confidence', ascending=True).reset_index(drop=True)
                        
                        window.populate_table_with_data(window.table_low, window.df_low)
                        window.populate_table_with_data(window.table_medium, window.df_medium)
                        window.populate_table_with_data(window.table_high, window.df_high)
                        
                        window.tab_widget.setTabText(0, f"🔴 Low Confidence (<50%) - {len(window.df_low)} patches")
                        window.tab_widget.setTabText(1, f"🟡 Medium Confidence (50-90%) - {len(window.df_medium)} patches")
                        window.tab_widget.setTabText(2, f"🟢 High Confidence (>90%) - {len(window.df_high)} patches")
                        
                        window.update_stats()
                        window.save_btn.setEnabled(True)
                        window.bulk_approve_btn.setEnabled(True)
                        window.info_label.setText(f"Auto-loaded: {os.path.basename(last_folder)}")
        except:
            pass  # Silently fail auto-load, user can manually load
    
    sys.exit(app.exec_())
