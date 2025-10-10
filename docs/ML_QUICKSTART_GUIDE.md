# ML Circle Classification - Quick Start Guide

## 🚀 Getting Started in 4 Steps

### Step 1: Generate Dataset (5 minutes)

Run the existing pipeline with the ML dataset generator stage added:

```bash
cd /Users/kaghatak/dev/July2025/pyqt

# Test with one OMR sheet first
python -c "
from image_processor import ImageProcessor
from pipeline.ml_dataset_generator_stage import MLDatasetGeneratorStage

processor = ImageProcessor()

# Add ML dataset generator to pipeline
ml_stage = MLDatasetGeneratorStage(processor)
processor.pipeline_manager.add_stage(ml_stage)

# Process your test image
result = processor.process_image_pipeline(
    'test_input_pdf/OMR_300DPI_pages/page_1.png',
    'test_input_pdf/OMR_300DPI_pages'
)

print('Dataset generated:', result.get('dataset_directory'))
"
```

**Expected Output:**
```
dataset/
├── patches/
│   ├── col1_q01_opt_a.png  (40x40 image)
│   ├── col1_q01_opt_b.png
│   └── ... (400 patches total)
├── metadata.csv
└── summary.json
```

---

### Step 2: Review Labels (15-30 minutes for 400 patches)

Launch the manual review tool:

```bash
python tools/manual_review_tool.py
```

**Keyboard Shortcuts:**
- `1` - Mark as "Marked"
- `2` - Mark as "Unmarked"  
- `3` - Mark as "Unsure"
- `D` - Save & Next
- `A` - Previous
- `S` - Skip

**Tips:**
- Review 50-100 patches to start
- Focus on ambiguous cases (fill_ratio 0.15-0.35)
- Mark clearly filled circles as "marked"
- Mark empty circles as "unmarked"
- Use "unsure" for edge cases (will be excluded from training)

---

### Step 3: Train Model (5-10 minutes)

Install PyTorch if not already installed:

```bash
pip install torch torchvision matplotlib scikit-learn
```

Train the model:

```bash
python ml/train_circle_classifier.py test_input_pdf/OMR_300DPI_pages/page_1_ml_dataset
```

**Expected Output:**
```
Epoch [1/50] | Train Loss: 0.6543 | Val Loss: 0.5123 | Val Acc: 82.34%
Epoch [2/50] | Train Loss: 0.4321 | Val Loss: 0.3456 | Val Acc: 88.12%
...
Epoch [50/50] | Train Loss: 0.1234 | Val Loss: 0.2345 | Val Acc: 96.78%

✅ Best model saved to: .../trained_model/best_model.pth
   Best validation accuracy: 96.78%
```

---

### Step 4: Use Model in Pipeline

Create a new pipeline stage to use the trained model:

```python
# pipeline/ml_circle_classification_stage.py

import torch
from .base_stage import PipelineStage
from ..ml.train_circle_classifier import CircleCNN

class MLCircleClassificationStage(PipelineStage):
    """Stage: Classify circles using trained ML model"""
    
    def __init__(self, processor_instance, model_path):
        super().__init__(processor_instance)
        self.model = CircleCNN()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def process(self, image_path, context):
        # Extract patches for all grid circles
        # Run inference
        # Return predictions
        pass
```

---

## 📊 Collecting More Data

To improve model accuracy, collect data from multiple OMR sheets:

```bash
# Process 50 OMR sheets to get 20,000 patches
for i in {1..50}; do
    python process_omr_sheet.py sheet_${i}.png
done

# Combine datasets
python tools/combine_datasets.py --input-dirs sheet_*_ml_dataset --output combined_dataset
```

---

## 🎯 Model Performance Targets

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Accuracy | 90% | 95% | 98%+ |
| Precision | 90% | 95% | 98%+ |
| Recall | 90% | 95% | 98%+ |
| False Positives | <5% | <2% | <1% |
| False Negatives | <5% | <2% | <1% |

---

## 🔧 Troubleshooting

### Low Accuracy (<90%)

**Problem:** Model not learning properly

**Solutions:**
1. Check label quality - review more patches manually
2. Increase dataset size (need 1000+ patches minimum)
3. Check for class imbalance (adjust class weights)
4. Try different threshold values in traditional classifier

### Model Overfitting

**Problem:** High train accuracy, low val accuracy

**Solutions:**
1. Increase dropout rate (0.5 → 0.6)
2. Add more data augmentation
3. Reduce model complexity
4. Add more training data

### Inference Too Slow

**Problem:** Model takes too long on 400 circles

**Solutions:**
1. Use batch inference (process 32 circles at once)
2. Convert model to ONNX for faster inference
3. Use GPU if available
4. Consider quantization for mobile deployment

---

## 📈 Next Steps

### Week 1: Initial Model
- [x] Generate dataset from 10-20 sheets
- [x] Review 500-1000 patches
- [x] Train initial model
- [x] Achieve 90%+ accuracy

### Week 2: Refinement
- [ ] Collect data from 50+ sheets
- [ ] Review edge cases
- [ ] Retrain with larger dataset
- [ ] Achieve 95%+ accuracy

### Week 3: Production
- [ ] Integrate into main pipeline
- [ ] Add confidence thresholding
- [ ] Set up automated retraining
- [ ] Deploy to production

### Week 4: Monitoring
- [ ] Collect feedback on predictions
- [ ] Identify failure modes
- [ ] Continuously improve dataset
- [ ] Retrain monthly

---

## 🎓 Understanding the Model

### Input
- 40×40 grayscale image of circle patch
- Normalized to [0, 1]

### Architecture
```
Input (1×40×40)
    ↓
Conv2D(32, 3×3) + ReLU + MaxPool → (32×20×20)
    ↓
Conv2D(64, 3×3) + ReLU + MaxPool → (64×10×10)
    ↓
Conv2D(128, 3×3) + ReLU + MaxPool → (128×5×5)
    ↓
Flatten → (3200)
    ↓
Dense(128) + ReLU + Dropout(0.5)
    ↓
Dense(2) → [unmarked_prob, marked_prob]
```

### Output
- 2 values: [probability_unmarked, probability_marked]
- Use argmax to get prediction
- Use max probability as confidence score

---

## 💡 Tips for Success

1. **Start Small**: Test with 1-2 sheets first
2. **Quality over Quantity**: 100 well-labeled patches > 1000 poorly labeled
3. **Focus on Edge Cases**: Review ambiguous circles carefully
4. **Monitor Confidence**: Low confidence predictions need review
5. **Iterate**: Model improves with more diverse data
6. **Track Metrics**: Log predictions to identify failure patterns

---

## 📞 Need Help?

Common issues and solutions are in the main ML_PIPELINE_PROPOSAL.md file.

For questions, check:
- Dataset format: metadata.csv should have all required columns
- Model loading: Ensure PyTorch version compatibility
- Path issues: Use absolute paths for datasets

