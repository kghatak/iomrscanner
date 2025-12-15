# Automated Pipeline Processing

This document explains how to use the automated pipeline processing script that runs the entire OMR processing workflow without the UI.

## Overview

The automation script (`automate_pipeline.py`) provides a command-line interface to:
1. Take a PDF file as input
2. Extract images from the PDF
3. Run all pipeline stages automatically
4. Generate organized results and reports

## Quick Start

### Basic Usage

```bash
python automate_pipeline.py <pdf_path>
```

### With Custom Output Folder

```bash
python automate_pipeline.py <pdf_path> <output_folder>
```

### Examples

```bash
# Process a PDF with default output folder
python automate_pipeline.py test_input_pdf/OMR_300DPI.pdf

# Process a PDF with custom output folder
python automate_pipeline.py test_input_pdf/OMR_300DPI.pdf my_results/

# Process a PDF and keep temporary files
python automate_pipeline.py test_input_pdf/OMR_300DPI.pdf --keep-temp
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `pdf_path` | **Required.** Path to the PDF file containing OMR sheets |
| `output_folder` | **Optional.** Output folder for results (defaults to timestamped folder) |
| `--keep-temp` | **Optional.** Keep temporary extracted images (default: cleanup after processing) |
| `--help` | Show help message and usage examples |

## Output Structure

The automation script creates the following folder structure:

```
output_folder/
├── success/                          # Successfully processed images
│   ├── 12345.png                    # Processed image with success overlay
│   ├── 12345_student_data.json      # Student data from API (if available)
│   └── 67890.png
├── error/                            # Failed processing images
│   ├── 99999.png                    # Error image with error overlay
│   └── 99999_student_data.json      # Error response data (if available)
└── logs/                             # Processing logs and reports
    ├── processing_report.json        # Detailed JSON report
    └── processing_summary.txt        # Human-readable summary
```

## Pipeline Stages

The automation runs the following stages in order:

1. **ArUco Check Stage** - Detects ArUco markers
2. **Orientation Check Stage** - Checks and corrects image orientation
3. **Roll Number Extraction Stage** - Extracts roll number from the sheet
4. **Fetch Student Stage** - Fetches student data from API
5. **OMR Processing Stage** - Processes the OMR sheet
6. **OMR Answer Extraction Stage** - Extracts marked answers
7. **Answer Validation Stage** - Validates extracted answers
8. **API Upload Stage** - Uploads results to API

## JSON Output Files

### Success Files (`{roll_number}_student_data.json`)
Contains the complete student data returned by the API when status code is 200:

```json
{
  "student_id": "12345",
  "name": "John Doe",
  "class": "10A",
  "subjects": [...],
  "marks": {...}
}
```

### Error Files (`{roll_number}_student_data.json`)
Contains error information when API calls fail:

```json
{
  "status_code": 404,
  "error": "Student not found",
  "roll_number": "12345",
  "url": "https://api.example.com/result/roll/12345",
  "response_text": "Student not found in database"
}
```

## Processing Report

The automation generates two types of reports:

### 1. JSON Report (`processing_report.json`)
Detailed machine-readable report with:
- Pipeline summary statistics
- Individual image processing results
- Pipeline stage information
- Timing data

### 2. Text Summary (`processing_summary.txt`)
Human-readable summary with:
- Processing statistics
- Success/failure breakdown
- Error details for failed images
- Pipeline stage list

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All images processed successfully |
| 1 | One or more images failed processing |
| 1 | Fatal error (file not found, etc.) |

## Programmatic Usage

You can also use the automation programmatically:

```python
from automate_pipeline import AutomatedPipelineProcessor

# Initialize processor
processor = AutomatedPipelineProcessor("my_output_folder")

# Run full pipeline
results = processor.run_full_pipeline("path/to/omr_sheet.pdf")

# Check results
print(f"Processed {results['total_images']} images")
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
```

## Testing

Use the test script to verify the automation works:

```bash
python test_automation.py
```

This will process the test PDF in `test_input_pdf/OMR_300DPI.pdf` and save results to `test_results/`.

## Requirements

- Python 3.7+
- All dependencies from `requirements.txt`
- Poppler installed (for PDF processing)
- Valid PDF file with OMR sheets

## Troubleshooting

### Common Issues

1. **PDF not found**
   ```
   ❌ ERROR: PDF file not found: /path/to/file.pdf
   ```
   - Check the file path is correct
   - Ensure the file exists and is readable

2. **No images extracted**
   ```
   ❌ ERROR: No images extracted from PDF
   ```
   - Check if Poppler is installed correctly
   - Verify the PDF contains images (not just text)

3. **Pipeline stage failures**
   - Check the error logs in the `logs/` folder
   - Review the processing summary for specific error messages
   - Ensure the OMR sheet format matches expected structure

### Debug Mode

For detailed debugging, you can modify the script to add more verbose logging or run individual stages manually.

## Performance

- Processing time depends on image size and complexity
- Typical processing: 10-30 seconds per image
- Large PDFs with many pages may take several minutes
- Results are saved incrementally, so partial results are preserved if processing is interrupted

## Integration

The automation script can be integrated into:
- Batch processing workflows
- CI/CD pipelines
- Scheduled tasks (cron jobs)
- Web applications
- Desktop applications

## Support

For issues or questions:
1. Check the processing logs in the `logs/` folder
2. Review the error messages in the console output
3. Verify all dependencies are installed correctly
4. Test with the provided sample PDF first
