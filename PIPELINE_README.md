# Comprehensive Image Processing Pipeline

This document describes the comprehensive image processing pipeline that has been implemented for OMR sheet processing.

## Overview

The pipeline processes images through 5 distinct stages, with robust error handling and categorization. If any stage fails, the image is marked with a red line and moved to an error folder, while processing continues with the next image.

## Pipeline Stages

### 1. ✅ ArUco Marker Check
- **Purpose**: Verify that basic ArUco markers are present in the image
- **Requirements**: Minimum 5 ArUco markers detected
- **Failure**: Image moved to error folder if insufficient markers found

### 2. 🔄 Image Orientation Check & Rotation
- **Purpose**: Detect and correct tilted/rotated images
- **Method**: Uses ArUco marker positions to determine orientation
- **Output**: Rotated image if correction needed
- **Failure**: Image moved to error folder if orientation detection fails

### 3. 🆔 Roll Number Extraction
- **Purpose**: Extract exam roll number from the image using OCR
- **Method**: Uses Tesseract OCR to extract text and parse roll number patterns
- **Patterns**: Looks for "Roll No:", "Roll Number:", or 6-10 digit numbers
- **Failure**: Image moved to error folder if roll number cannot be extracted

### 4. 📝 OMR Sheet Processing
- **Purpose**: Process the OMR sheet and extract answer data
- **Method**: Analyzes ArUco marker positions and patterns
- **Output**: Structured OMR data with roll number, marker positions, and timestamps
- **Failure**: Image moved to error folder if OMR processing fails

### 5. 📤 API Upload
- **Purpose**: Upload processed data to external API
- **Method**: Currently simulated (can be replaced with actual API calls)
- **Output**: Upload confirmation with upload ID
- **Failure**: Image moved to error folder if upload fails

## Usage

### Through the UI

1. **Select Folder**: Choose a folder containing images to process
2. **Configure Markers**: Select expected ArUco marker IDs (1-20)
3. **Start Pipeline**: Click "🚀 Start Pipeline Processing" button
4. **Monitor Progress**: Watch real-time progress in the processing log
5. **Review Results**: Check success/error folders for processed images

### Through Code

```python
from image_processor import ImageProcessor

# Initialize processor
processor = ImageProcessor()

# Process single image through pipeline
result = processor.process_image_pipeline(
    image_path="path/to/image.jpg",
    output_folder="path/to/output"
)

# Check results
if result['success']:
    print("Pipeline completed successfully!")
    stages = result['stages']
    roll_number = stages['roll_number_extraction']['roll_number']
    print(f"Roll number: {roll_number}")
else:
    print(f"Failed at stage: {result['error_stage']}")
    print(f"Error: {result['error_message']}")
```

## Output Structure

### Success Folder
```
pipeline_processing_results/
├── success/
│   ├── image1_processed.jpg
│   ├── image2_processed.jpg
│   └── ...
```

### Error Folder
```
pipeline_processing_results/
├── error/
│   ├── image1_ERROR.jpg  # Marked with red line
│   ├── image2_ERROR.jpg  # Marked with red line
│   └── ...
```

### Result Data Structure

```python
{
    "filename": "image.jpg",
    "success": True/False,
    "stages": {
        "aruco_check": {
            "success": True,
            "detected_markers": [1, 2, 3, 4, 5],
            "detection_info": {...}
        },
        "orientation_check": {
            "success": True,
            "rotation_applied": 0,
            "rotated_image_path": "path/to/rotated.jpg"
        },
        "roll_number_extraction": {
            "success": True,
            "roll_number": "123456",
            "extracted_text": "Roll No: 123456"
        },
        "omr_processing": {
            "success": True,
            "omr_data": {
                "roll_number": "123456",
                "detected_markers": [1, 2, 3, 4, 5],
                "marker_positions": [...],
                "processing_timestamp": "2024-01-01 12:00:00",
                "image_path": "path/to/image.jpg"
            }
        },
        "api_upload": {
            "success": True,
            "upload_id": "upload_1704067200",
            "api_response": {...}
        }
    },
    "error_stage": None,  # Only present if failed
    "error_message": None,  # Only present if failed
    "output_path": "path/to/processed/image.jpg",
    "api_upload_success": True
}
```

## Error Handling

### Error Marking
- Failed images are marked with a red horizontal line
- Error text is added to the image showing the failed stage
- Images are saved to the error folder with "_ERROR" suffix

### Error Categories
- **aruco_check**: Insufficient ArUco markers detected
- **orientation_check**: Cannot determine image orientation
- **roll_number_extraction**: Cannot extract roll number from image
- **omr_processing**: OMR sheet processing failed
- **api_upload**: API upload failed
- **pipeline_exception**: Unexpected error in pipeline

## Configuration

### ArUco Markers
- **Dictionary**: DICT_4X4_50 (valid IDs: 0-49)
- **Default Expected**: Markers 1-20
- **Minimum Required**: 5 markers for basic validation

### OCR Settings
- **Engine**: Tesseract OCR
- **Language**: English (default)
- **Patterns**: Configurable roll number patterns

### API Integration
- **Current**: Simulated upload
- **Customization**: Replace `_simulate_api_upload()` with actual API calls
- **Authentication**: Add API keys and authentication as needed

## Testing

### Run Test Suite
```bash
python test_pipeline.py
```

### Test Individual Stages
```python
from image_processor import ImageProcessor

processor = ImageProcessor()

# Test individual stages
stage1_result = processor._stage1_check_aruco_markers("image.jpg")
stage2_result = processor._stage2_check_and_rotate_image("image.jpg")
stage3_result = processor._stage3_extract_roll_number("image.jpg")
stage4_result = processor._stage4_process_omr_sheet("image.jpg", "123456")
stage5_result = processor._stage5_upload_to_api(omr_data, "123456")
```

## Customization

### Adding New Stages
1. Add new stage method to `ImageProcessor` class
2. Update `process_image_pipeline()` method
3. Add stage to pipeline flow
4. Update error handling

### Modifying Roll Number Patterns
Edit the `_parse_roll_number()` method to add new patterns:

```python
patterns = [
    r'Roll\s*[Nn]o[.:]\s*(\d+)',
    r'Roll\s*[Nn]umber[.:]\s*(\d+)',
    r'(\d{6,10})',  # 6-10 digit number
    r'Your\s*Custom\s*Pattern\s*(\d+)',  # Add custom pattern
]
```

### Custom API Integration
Replace `_simulate_api_upload()` with actual API calls:

```python
def _upload_to_real_api(self, omr_data: Dict) -> Dict:
    import requests
    
    try:
        response = requests.post(
            'https://your-api-endpoint.com/upload',
            json=omr_data,
            headers={'Authorization': 'Bearer YOUR_API_KEY'}
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "upload_id": response.json().get('id'),
                "message": "Upload successful"
            }
        else:
            return {
                "success": False,
                "error": f"API error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }
```

## Dependencies

### Required Python Packages
```bash
pip install opencv-python pytesseract numpy pillow
```

### System Dependencies
- **Tesseract OCR**: Required for text extraction
- **OpenCV**: Required for image processing and ArUco detection
- **NumPy**: Required for numerical operations

### Installation
```bash
# macOS
brew install tesseract poppler

# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# Windows
# Download and install Tesseract from GitHub releases
```

## Performance Considerations

### Batch Processing
- Images are processed sequentially to avoid memory issues
- Progress is reported for each image
- Cancellation is supported during processing

### Memory Management
- Images are loaded and processed one at a time
- Temporary files are cleaned up automatically
- Large images are handled efficiently

### Error Recovery
- Failed images don't stop the entire batch
- Detailed error logging for debugging
- Error images are preserved for manual review

## Troubleshooting

### Common Issues

1. **No ArUco markers detected**
   - Check image quality and lighting
   - Verify ArUco dictionary matches markers
   - Ensure minimum marker size requirements

2. **OCR fails to extract roll number**
   - Improve image quality and contrast
   - Check if roll number text is clearly visible
   - Verify Tesseract installation

3. **API upload fails**
   - Check network connectivity
   - Verify API endpoint and authentication
   - Review API response for error details

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export DEBUG_PIPELINE=1
python your_script.py
```

## Future Enhancements

### Planned Features
- **Parallel Processing**: Process multiple images simultaneously
- **Advanced OCR**: Support for multiple languages and fonts
- **Machine Learning**: Improved roll number detection
- **Real-time Processing**: Stream processing for live applications
- **Cloud Integration**: Direct upload to cloud storage

### Extensibility
The pipeline is designed to be easily extensible:
- New stages can be added without modifying existing code
- Custom validation rules can be implemented
- Different output formats can be supported
- Multiple API endpoints can be configured
