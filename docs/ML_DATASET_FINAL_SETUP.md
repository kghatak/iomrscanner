# ML Dataset Generator - Final Setup

## ✅ What's Been Fixed

### 1. **Added to Default Pipeline (with Safe Fallback)**

The ML Dataset Generator is now part of the **default pipeline**, but with intelligent error handling:

- ✅ **If pandas is available**: Stage runs automatically (Position 6)
- ✅ **If pandas has issues**: Stage is skipped gracefully, pipeline continues
- ✅ **Clear messaging**: You'll see exactly why it was skipped

**Current Status (Without fresh environment):**
```
[PipelineManager] ⚠️  ML Dataset Generator stage skipped
[PipelineManager]    Reason: numpy.dtype size changed...
[PipelineManager]    To enable: Run ./setup_fresh_env.sh to fix dependencies
```

**After Running setup_fresh_env.sh:**
```
[PipelineManager] ✅ ML Dataset Generator stage added (pandas available)
Stage 6: ml_dataset_generator - Generate ML training dataset
```

---

### 2. **Improved Patch Extraction**

Now uses **perfect normalized grid circles**:

#### What Changed:
- ✅ Extracts patches from exact (x_mean, y_mean) grid positions
- ✅ Uses consistent r_mean per column
- ✅ Perfect centering in every patch
- ✅ Consistent patch sizes
- ✅ Better edge handling with white padding
- ✅ Precise circular mask (85% of radius for analysis)

#### Technical Details:
```python
# Each patch is extracted using:
- Center: (x_mean, y_mean) from normalized grid
- Radius: r_mean for the column
- Patch size: 2.5 × diameter (about 80×80 pixels)
- Mask radius: 0.85 × r_mean (focuses on filled area)
```

---

### 3. **Complete Pipeline Flow**

```
1. ArUco Check         ← Detect 20 markers
2. Orientation Check   ← Rotate if needed
3. Roll Number         ← Extract roll number (OCR)
4. OMR Processing      ← Find column rectangles
5. Answer Extraction   ← Create 4×25 normalized grid
6. ML Dataset Gen      ← Extract 400 perfect patches [OPTIONAL]
7. API Upload          ← Upload results
```

---

## 🚀 How to Enable ML Dataset Generation

### Step 1: Run Fresh Environment Setup

This will fix all pandas/numpy compatibility issues:

```bash
cd /Users/kaghatak/dev/July2025/pyqt
./setup_fresh_env.sh
```

**This script will:**
- ✅ Remove old broken environments
- ✅ Create fresh venv
- ✅ Install compatible versions of all dependencies
- ✅ Test all imports (including pandas)
- ✅ Takes ~3-5 minutes

### Step 2: Activate Environment

```bash
source venv/bin/activate
```

### Step 3: Verify ML Stage is Active

```bash
python -c "
from image_processor import ImageProcessor
processor = ImageProcessor()
stages = [s.get_stage_name() for s in processor.pipeline_manager.stages]
print('ML Dataset Generator:', 'ml_dataset_generator' in stages)
"
```

Should output: `ML Dataset Generator: True`

---

## 📊 Using the ML Dataset Generator

### Automatic Generation (Recommended)

Just run your normal pipeline - datasets are generated automatically!

```bash
# Activate environment first
source venv/bin/activate

# Process OMR image - dataset generated automatically
python -c "
from image_processor import ImageProcessor

processor = ImageProcessor()
result = processor.process_image_pipeline(
    'test_input_pdf/OMR_300DPI_pages/page_1.png',
    'test_input_pdf/OMR_300DPI_pages'
)

print('Success:', result['success'])

# Check if ML dataset was generated
if 'ml_dataset_generator' in result['stages']:
    ml_result = result['stages']['ml_dataset_generator']
    print('Dataset:', ml_result.get('dataset_directory'))
    print('Patches:', ml_result.get('total_patches'))
"
```

### Manual Script (Alternative)

```bash
python generate_ml_dataset.py path/to/image.png
```

---

## 📁 Output Structure

After processing an OMR sheet, you'll get:

```
your_folder/
├── page_1.png
├── page_1_visualization.png          ← Rectangles + blue grid
├── page_1_visualization_circles.png  ← Rectangles + green/red circles
└── page_1_ml_dataset/                ← NEW! ML training data
    ├── patches/
    │   ├── col1_q01_opt_a.png (400 patches total)
    │   └── ...
    ├── metadata.csv
    └── summary.json
```

---

## 🎯 Next Steps After Dataset Generation

### 1. Review Labels (Optional but Recommended)

```bash
python tools/manual_review_tool.py
# Select the dataset folder
# Review and correct labels
# Save changes
```

### 2. Train Model

```bash
python ml/train_circle_classifier.py path/to/dataset
# Takes 5-10 minutes
# Outputs: best_model.pth, training_curves.png
```

### 3. Use Model in Production

(Integration code to be added later)

---

## 🔍 Troubleshooting

### Issue: ML stage still not added after setup

**Check pandas installation:**
```bash
source venv/bin/activate
python -c "import pandas; print('Pandas:', pandas.__version__)"
```

If it fails, reinstall:
```bash
pip uninstall pandas numpy -y
pip install numpy==1.24.3 pandas==2.0.3 --no-cache-dir
```

### Issue: Dataset folder not created

**Verify stage ran:**
```bash
# Look for these lines in output:
[MLDatasetGeneratorStage] ====== Starting
[MLDatasetGeneratorStage] ✅ SUCCESS
```

If missing, ML stage may have been skipped or failed.

### Issue: Patches look wrong or misaligned

**This is fixed!** The new version uses perfect grid circles. If you see:
- Circles perfectly centered in patches ✅
- Consistent sizes within each column ✅
- Some patches with white padding near edges ✅

This is correct behavior!

---

## 📈 Quality Comparison

### Before (Old System):
- ❌ Variable patch sizes
- ❌ Imperfect centering
- ❌ Used detected circles (noisy)
- ❌ Manual pipeline configuration

### After (Current System):
- ✅ Consistent patch sizes
- ✅ Perfect centering on normalized grid
- ✅ Uses ideal grid positions (clean)
- ✅ Automatic with error handling

---

## 💡 Key Points to Remember

1. **Run setup_fresh_env.sh first** - Fixes all dependency issues
2. **ML stage is optional** - Pipeline works without it
3. **Automatic generation** - No manual intervention needed
4. **High-quality data** - Uses perfect normalized grid circles
5. **400 patches per image** - 4 columns × 25 questions × 4 options

---

## ✅ Summary

**What You Have Now:**
- ✅ ML Dataset Generator integrated into default pipeline
- ✅ Graceful fallback if pandas unavailable
- ✅ Improved patch extraction using perfect grid circles
- ✅ Automatic dataset generation with every OMR processing
- ✅ Complete documentation and setup scripts

**To Get Started:**
```bash
# 1. Fix environment
./setup_fresh_env.sh

# 2. Activate
source venv/bin/activate

# 3. Process images (datasets generated automatically!)
python main.py
```

**That's it!** 🎉

Every OMR image you process will now automatically generate a high-quality ML training dataset using the perfect normalized grid circles!

