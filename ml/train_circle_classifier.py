#!/usr/bin/env python3
"""
Train CNN Model for OMR Circle Classification

Simple PyTorch CNN to classify circles as marked or unmarked.
"""

import os
import sys
import pandas as pd
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from typing import Tuple


class CircleDataset(Dataset):
    """PyTorch Dataset for circle patches"""
    
    def __init__(self, df: pd.DataFrame, patches_dir: str, transform=None):
        self.df = df
        self.patches_dir = patches_dir
        self.transform = transform
        
        # Use reviewed_label if available, else initial_label
        self.labels = []
        for idx, row in df.iterrows():
            label = row.get('reviewed_label', '')
            if not label or label == 'unsure':
                label = row['initial_label']
            self.labels.append(1 if label == 'marked' else 0)
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # Load image
        img_path = os.path.join(self.patches_dir, row['image_name'])
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        # Resize to fixed size
        img = cv2.resize(img, (40, 40))
        
        # Normalize to [0, 1]
        img = img.astype(np.float32) / 255.0
        
        # Add channel dimension: (40, 40) -> (1, 40, 40)
        img = np.expand_dims(img, axis=0)
        
        # Data augmentation (simple)
        if self.transform:
            # Random rotation
            if np.random.rand() > 0.5:
                angle = np.random.uniform(-5, 5)
                center = (20, 20)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                img = cv2.warpAffine(img[0], M, (40, 40))
                img = np.expand_dims(img, axis=0)
            
            # Random brightness
            if np.random.rand() > 0.5:
                brightness = np.random.uniform(0.8, 1.2)
                img = np.clip(img * brightness, 0, 1)
        
        img_tensor = torch.from_numpy(img).float()
        label_tensor = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return img_tensor, label_tensor


class CircleCNN(nn.Module):
    """Simple CNN for binary classification"""
    
    def __init__(self):
        super(CircleCNN, self).__init__()
        
        # Conv layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        
        # After 3 pooling layers: 40 -> 20 -> 10 -> 5
        # Feature map size: 128 * 5 * 5 = 3200
        self.fc1 = nn.Linear(128 * 5 * 5, 128)
        self.fc2 = nn.Linear(128, 2)  # Binary: marked, unmarked
    
    def forward(self, x):
        # Conv block 1
        x = self.relu(self.conv1(x))
        x = self.pool(x)  # 40 -> 20
        
        # Conv block 2
        x = self.relu(self.conv2(x))
        x = self.pool(x)  # 20 -> 10
        
        # Conv block 3
        x = self.relu(self.conv3(x))
        x = self.pool(x)  # 10 -> 5
        
        # Flatten
        x = x.view(-1, 128 * 5 * 5)
        
        # FC layers
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


def train_model(dataset_dir: str, output_dir: str, epochs=50, batch_size=32):
    """Train the circle classification model"""
    
    print("=" * 80)
    print("🚀 Training OMR Circle Classifier")
    print("=" * 80)
    
    # Load metadata
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    df = pd.read_csv(metadata_path)
    
    # Filter out unsure labels
    df_clean = df[df.get('reviewed_label', df['initial_label']) != 'unsure'].copy()
    
    print(f"\nDataset Statistics:")
    print(f"  Total patches: {len(df_clean)}")
    
    # Check label distribution
    labels = []
    for idx, row in df_clean.iterrows():
        label = row.get('reviewed_label', '')
        if not label:
            label = row['initial_label']
        labels.append(label)
    
    marked_count = labels.count('marked')
    unmarked_count = labels.count('unmarked')
    
    print(f"  Marked: {marked_count} ({marked_count/len(labels)*100:.1f}%)")
    print(f"  Unmarked: {unmarked_count} ({unmarked_count/len(labels)*100:.1f}%)")
    
    # Train/val/test split
    train_df, test_df = train_test_split(df_clean, test_size=0.2, random_state=42, stratify=labels)
    train_df, val_df = train_test_split(train_df, test_size=0.15, random_state=42)
    
    print(f"\n  Train: {len(train_df)}")
    print(f"  Validation: {len(val_df)}")
    print(f"  Test: {len(test_df)}")
    
    # Create datasets
    patches_dir = os.path.join(dataset_dir, "patches")
    
    train_dataset = CircleDataset(train_df, patches_dir, transform=True)
    val_dataset = CircleDataset(val_df, patches_dir, transform=False)
    test_dataset = CircleDataset(test_df, patches_dir, transform=False)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nUsing device: {device}")
    
    model = CircleCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    print(f"\n{'='*80}")
    print("Training Progress")
    print(f"{'='*80}\n")
    
    train_losses = []
    val_losses = []
    val_accuracies = []
    
    best_val_acc = 0.0
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        train_losses.append(train_loss)
        
        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100 * correct / total
        
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        
        print(f"Epoch [{epoch+1}/{epochs}] | "
              f"Train Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs(output_dir, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(output_dir, 'best_model.pth'))
    
    # Test evaluation
    print(f"\n{'='*80}")
    print("Test Set Evaluation")
    print(f"{'='*80}\n")
    
    model.load_state_dict(torch.load(os.path.join(output_dir, 'best_model.pth')))
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Classification report
    print(classification_report(all_labels, all_preds, 
                                target_names=['unmarked', 'marked']))
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    print("\nConfusion Matrix:")
    print(cm)
    
    # Plot training curves
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(val_accuracies, label='Val Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.title('Validation Accuracy')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_curves.png'))
    print(f"\n📊 Training curves saved to: {output_dir}/training_curves.png")
    
    print(f"\n✅ Best model saved to: {output_dir}/best_model.pth")
    print(f"   Best validation accuracy: {best_val_acc:.2f}%")
    
    return model


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_circle_classifier.py <dataset_directory>")
        print("Example: python train_circle_classifier.py test_input_pdf/OMR_300DPI_pages/page_1_ml_dataset")
        sys.exit(1)
    
    dataset_dir = sys.argv[1]
    output_dir = os.path.join(dataset_dir, "trained_model")
    
    model = train_model(dataset_dir, output_dir, epochs=50, batch_size=32)

