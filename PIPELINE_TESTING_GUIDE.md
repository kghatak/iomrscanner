# Pipeline Testing Guide - Single Image (No UI)

This guide explains how to test the OMR pipeline on a single PNG image without launching the UI, which is useful for quick iteration and internal testing.

## Quick Start

```bash
# Basic usage
python test_single_image_pipeline.py path/to/image.png

# With custom output folder
python test_single_image_pipeline.py path/to/image.png ./my_results

# With custom ArUco markers
python test_single_image_pipeline.py image.png --markers "1-20"
python test_single_image_pipeline.py image.png --markers "1,2,3,4,5,10,15"
```

## What This Script Does

The `test_single_image_pipeline.py` script **replicates exactly** what the UI does when processing an image:

1. ✅ Initializes `ImageProcessor` with the same configuration
2. ✅ Sets expected ArUco markers (default: 1-20, same as UI)
3. ✅ Runs the **complete pipeline** through all stages:
   - ArUco Check
   - Orientation Check
   - Roll Number Extraction
   - Fetch Student Data
   - OMR Processing
   - OMR Answer Extraction
   - Answer Validation
   - API Upload
4. ✅ Saves results to `success/` or `error/` folders (same structure as UI)
5. ✅ Prints detailed stage-by-stage results

## Pipeline Stages (No Changes Needed)

✅ **Good news**: The pipeline is already designed to work **completely independently** of the UI!

### No UI Dependencies

All pipeline stages use only:
- OpenCV (`cv2`)
- NumPy
- Standard Python libraries
- No PyQt5 or UI components

The pipeline stages are in `pipeline/` and are **UI-agnostic**:
- `aruco_check_stage.py`
- `orientation_check_stage.py`
- `roll_number_extraction_stage.py`
- `fetch_student_stage.py`
- `omr_processing_stage.py`
- `omr_answer_extraction_stage.py`
- `answer_validation_stage.py`
- `api_upload_stage.py`

### How UI Uses Pipeline

The UI (`ui/results_panel.py`) simply calls:
```python
processor = ImageProcessor()
processor.set_expected_markers([1, 2, 3, ..., 20])
result = processor.process_image_pipeline(image_path, output_folder)
```

**This is exactly what the test script does!**

## Example Output

```
================================================================================
  OMR Pipeline - Single Image Test (No UI)
================================================================================

📷 Image: test_input_pdf/OMR_300DPI_pages/page_1.png
📂 Output: /path/to/pipeline_results_20250115_143022
🎯 Expected ArUco Markers: [1, 2, 3, ..., 20]

🔧 Initializing ImageProcessor...
✅ ImageProcessor initialized
   Expected markers: [1, 2, 3, ..., 20]

--------------------------------------------------------------------------------
  Running Pipeline
--------------------------------------------------------------------------------

[PipelineManager] Starting pipeline processing...
[ArUcoCheckStage] Checking ArUco markers...
[OrientationCheckStage] Checking orientation...
...

--------------------------------------------------------------------------------
  Pipeline Results
--------------------------------------------------------------------------------

✅ Pipeline completed successfully!

📊 Stage Results:
  ✅ aruco_check
     Detected markers: [1, 2, 3, ..., 20]
  ✅ orientation_check
  ✅ roll_number_extraction
     🆔 Roll Number: JAMB24030041
  ✅ fetch_student
     Student: John Doe
     Class: 8
  ✅ omr_processing
  ✅ omr_answer_extraction
     Marked answers: 45
  ✅ answer_validation
  ✅ api_upload
     📤 Upload ID: abc123

📁 Output image: /path/to/pipeline_results_20250115_143022/success/JAMB24030041.png
🆔 Roll Number: JAMB24030041
📤 API Upload: Success (ID: abc123)

================================================================================
  ✅ SUCCESS - Pipeline completed
================================================================================
📂 Check results in: /path/to/pipeline_results_20250115_143022
   - Success images: /path/to/pipeline_results_20250115_143022/success
   - Error images: /path/to/pipeline_results_20250115_143022/error
```

## Command-Line Options

```bash
python test_single_image_pipeline.py --help
```

**Arguments:**
- `image_path` (required): Path to PNG/image file
- `output_folder` (optional): Output folder (defaults to timestamped folder)
- `--markers` (optional): Expected ArUco marker IDs
  - Range format: `--markers "1-20"` (default)
  - List format: `--markers "1,2,3,4,5"`

## Comparison: UI vs Test Script

| Feature | UI (`ui/results_panel.py`) | Test Script (`test_single_image_pipeline.py`) |
|---------|---------------------------|----------------------------------------------|
| Initialize ImageProcessor | ✅ | ✅ |
| Set expected markers | ✅ (from UI checkboxes) | ✅ (from `--markers` arg) |
| Run full pipeline | ✅ | ✅ |
| Save to success/error folders | ✅ | ✅ |
| Show stage results | ✅ (in UI log) | ✅ (in console) |
| Handle errors | ✅ | ✅ |
| API upload | ✅ | ✅ |

**Result**: Both use the **exact same pipeline code path**!

## Troubleshooting

### "Required dependencies not available"
```bash
pip install opencv-python pytesseract numpy
```

### "Image file not found"
- Check the path is correct
- Use absolute path if relative path doesn't work

### Pipeline fails at specific stage
- Check the error message in the output
- Verify the image has the required ArUco markers
- Check API connectivity if failing at `api_upload` stage

## Integration with CI/CD

This script is perfect for automated testing:

```bash
# In CI/CD pipeline
python test_single_image_pipeline.py test_images/sample.png test_results
if [ $? -eq 0 ]; then
    echo "✅ Pipeline test passed"
else
    echo "❌ Pipeline test failed"
    exit 1
fi
```

## Summary

✅ **No changes needed** to pipeline files - they're already UI-independent  
✅ **Test script created** - `test_single_image_pipeline.py`  
✅ **Exact same behavior** as UI - uses identical code path  
✅ **Ready to use** - just run the script with a PNG file path

The pipeline architecture is well-designed with clear separation between UI and processing logic!

