# ML Pipeline for OMR Circle Classification

## Overview
Build a machine learning model to classify OMR circles as "marked" or "unmarked" using:
1. Traditional image processing for initial labeling
2. Manual review and correction
3. CNN-based binary classifier
4. Integration into existing pipeline

---

## Phase 1: Dataset Generation

### Step 1.1: Extract Circle Patches (30x30 or 40x40 pixels)
```
For each of the 400 grid circles:
1. Extract square patch centered at (x_mean, y_mean)
2. Size: 2.5 * r_mean × 2.5 * r_mean pixels
3. Normalize/preprocess
4. Save as individual image file
```

### Step 1.2: Traditional Threshold-Based Initial Labeling
```python
For each circle patch:
1. Convert to grayscale
2. Apply Gaussian blur
3. Calculate mean intensity in inner circle region
4. Apply adaptive thresholding or Otsu's method
5. Calculate fill ratio (dark pixels / total pixels)
6. Label:
   - "marked" if fill_ratio > threshold (e.g., 0.3)
   - "unmarked" if fill_ratio <= threshold
```

### Step 1.3: Dataset Structure
```
dataset/
├── patches/
│   ├── col1_q01_opt_a.png
│   ├── col1_q01_opt_b.png
│   ├── col1_q01_opt_c.png
│   ├── col1_q01_opt_d.png
│   └── ... (400 total)
├── metadata.csv
│   Columns: image_name, column, question, option, x, y, 
│            mean_intensity, fill_ratio, initial_label, 
│            reviewed_label, confidence
└── labels.json
```

### Step 1.4: Manual Review Interface
```
Simple PyQt GUI or Jupyter notebook:
- Display circle patch (zoomed)
- Show initial label
- Show metrics (intensity, fill_ratio)
- Buttons: "Marked", "Unmarked", "Unsure", "Skip", "Next"
- Save corrections to reviewed_label column
```

---

## Phase 2: ML Model Design

### Option A: Simple Custom CNN (Recommended for Start)
```
Model Architecture:
- Input: 40x40x1 (grayscale) or 40x40x3 (RGB)
- Conv2D(32, 3x3, ReLU) → MaxPool(2x2)
- Conv2D(64, 3x3, ReLU) → MaxPool(2x2)
- Conv2D(128, 3x3, ReLU) → MaxPool(2x2)
- Flatten
- Dense(128, ReLU) → Dropout(0.5)
- Dense(2, Softmax) [marked, unmarked]

Parameters: ~200K
Training time: 5-10 minutes on CPU
Accuracy expected: 95-98%
```

### Option B: Transfer Learning (If larger dataset)
```
Use MobileNetV2 or EfficientNet-B0:
- Pre-trained on ImageNet
- Remove top layers
- Add custom classifier head
- Fine-tune on OMR circles
- Better for complex marking patterns
```

### Option C: Ensemble (For Production)
```
Combine:
1. Custom CNN (60% weight)
2. Traditional threshold method (20% weight)
3. Gradient-based features (20% weight)
Results in more robust predictions
```

---

## Phase 3: Training Pipeline

### Data Preparation
```python
1. Train/Val/Test split: 70/15/15
2. Data Augmentation:
   - Random rotation (±5 degrees)
   - Random brightness/contrast adjustment
   - Gaussian noise
   - Slight scaling (0.95x to 1.05x)
3. Normalization: [0, 1] or [-1, 1]
4. Class balancing (if needed)
```

### Training Configuration
```python
- Loss: Binary Cross-Entropy
- Optimizer: Adam (lr=0.001)
- Batch size: 32-64
- Epochs: 50-100 (with early stopping)
- Metrics: Accuracy, Precision, Recall, F1
- Validation: Monitor on validation set
```

### Model Evaluation
```python
Key metrics:
- Overall accuracy
- Precision (avoid false positives)
- Recall (avoid false negatives)
- Confusion matrix
- Per-column/question analysis
- Confidence calibration
```

---

## Phase 4: Integration into Pipeline

### New Stage: `MLCircleClassificationStage`
```python
Input: Grid circles (400 per image)
Process:
  1. Extract patches for all grid circles
  2. Run ML model inference (batch mode)
  3. Get predictions + confidence scores
  4. Apply confidence threshold (e.g., 0.85)
  5. Flag low-confidence circles for review
Output:
  - Marked circles per column/question
  - Answer predictions (a/b/c/d per question)
  - Confidence scores
  - Ambiguous cases for human review
```

---

## Implementation Roadmap

### Week 1: Dataset Generation
- [ ] Create circle patch extraction tool
- [ ] Implement traditional threshold classifier
- [ ] Generate initial dataset (400 patches per image × N images)
- [ ] Build manual review interface

### Week 2: Model Development
- [ ] Prepare training data
- [ ] Implement CNN model
- [ ] Train and validate
- [ ] Optimize hyperparameters
- [ ] Save best model

### Week 3: Integration
- [ ] Create MLCircleClassificationStage
- [ ] Integrate with existing pipeline
- [ ] Add confidence-based filtering
- [ ] Test on real OMR sheets

### Week 4: Production
- [ ] Collect more data for fine-tuning
- [ ] Deploy model
- [ ] Monitor performance
- [ ] Set up retraining pipeline

---

## Technology Stack Recommendations

### Core ML Framework
```
Option 1: PyTorch (Recommended)
- Flexible, Pythonic
- Easy debugging
- Good for research and production

Option 2: TensorFlow/Keras
- Simpler API
- Good deployment options
- TFLite for mobile

Option 3: scikit-learn (for simple classifiers)
- Random Forest / SVM on hand-crafted features
- Fast training, good baseline
```

### Additional Libraries
```
- OpenCV: Image processing
- NumPy: Array operations
- Pandas: Metadata management
- Albumentations: Data augmentation
- Matplotlib/Seaborn: Visualization
- ONNX: Model conversion for deployment
```

---

## Dataset Size Recommendations

### Minimum Viable Dataset
- 50 OMR sheets × 400 circles = 20,000 patches
- Expect ~80% unmarked, ~20% marked (imbalanced)
- Apply oversampling or class weights

### Ideal Dataset
- 200-500 OMR sheets = 80,000-200,000 patches
- Cover variations:
  - Different marking styles (pen, pencil, marker)
  - Light/dark marks
  - Partial marks
  - Stray marks
  - Different scan qualities

---

## Expected Performance

### Traditional Threshold Method (Baseline)
- Accuracy: 85-92%
- Issues: Sensitive to scan quality, lighting

### Simple CNN Model
- Accuracy: 95-98%
- Fast inference: ~1ms per circle
- Robust to variations

### Ensemble Model
- Accuracy: 98-99%
- Better confidence calibration
- Handles edge cases

---

## Next Steps to Start

1. **Create dataset extraction script** (I can help implement this)
2. **Run on 10-20 sample OMR sheets** to get initial dataset
3. **Build review interface** for manual labeling
4. **Train initial model** and evaluate
5. **Iterate based on results**

Would you like me to implement:
- [ ] Circle patch extraction tool?
- [ ] Traditional threshold classifier?
- [ ] Manual review GUI?
- [ ] CNN model training script?
- [ ] All of the above?

