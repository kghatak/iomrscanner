# Stage Development Guide

## Overview

This guide explains how to test and develop individual pipeline stages independently. This approach allows you to:

- **Test each stage in isolation** without running the entire pipeline
- **Debug stage-specific issues** more effectively
- **Develop new stages** incrementally
- **Understand data flow** between stages
- **Plan development work** more systematically

## Available Development Tools

### 1. Command Line Testing (`test_single_stage.py`)

A command-line tool for quick stage testing and automation.

### 2. Interactive Development Environment (`develop_stage.py`)

An interactive menu-driven tool for iterative development and debugging.

### 3. Example Scripts (`examples/stage_development_examples.py`)

Comprehensive examples showing different testing scenarios.

## Quick Start

### Testing a Single Stage

```bash
# Test ArUco check stage with an image
python tests/test_single_stage.py aruco_check path/to/image.jpg

# Test with mock context data
python tests/test_single_stage.py omr_processing path/to/image.jpg \
  --mock-context '{"detected_markers": [1,2,3], "roll_number": "123456"}'

# Test all stages in sequence
python tests/test_single_stage.py all path/to/image.jpg

# Create a test image and test
python tests/test_single_stage.py aruco_check test.jpg --create-test-image
```

### Interactive Development

```bash
# Start interactive development environment
python tests/develop_stage.py
```

This opens a menu-driven interface where you can:
- Load images
- Test individual stages
- Test with mock context
- Test stage sequences
- View and modify context
- Create test images

## Development Workflow

### 1. **Understanding Stage Requirements**

Before developing a stage, understand what it needs:

```python
# Check stage description
from pipeline.aruco_check_stage import ArUcoCheckStage
stage = ArUcoCheckStage(processor)
print(stage.get_stage_description())  # "Check basic ArUco markers are present"
```

### 2. **Testing with Real Images**

Start with real images to understand current behavior:

```python
from tests.test_single_stage import SingleStageTester

tester = SingleStageTester()
result = tester.test_stage('aruco_check', 'path/to/real/image.jpg')
print(f"Success: {result['success']}")
print(f"Detected markers: {result.get('detected_markers', [])}")
```

### 3. **Testing with Mock Context**

Test stages that depend on previous stages:

```python
# Mock data from previous stages
mock_context = {
    "detected_markers": [1, 2, 3, 4, 5],
    "rotation_applied": 0,
    "rotated_image_path": "path/to/image.jpg",
    "roll_number": "123456"
}

result = tester.test_stage_with_mock_context('omr_processing', 'path/to/image.jpg', mock_context)
```

### 4. **Testing Stage Sequences**

Understand how data flows between stages:

```python
# Test first 3 stages
stages = ['aruco_check', 'orientation_check', 'roll_number_extraction']
results = tester.test_stage_sequence('path/to/image.jpg', stages)

# Check results
for stage_name, result in results.items():
    print(f"{stage_name}: {'Success' if result['success'] else 'Failed'}")
```

### 5. **Iterative Development**

Use the interactive environment for rapid iteration:

```bash
python tests/develop_stage.py
```

Then:
1. Load your test image
2. Test the stage you're working on
3. Modify the stage code
4. Test again
5. Repeat until satisfied

## Stage Development Examples

### Example 1: Testing ArUco Detection

```python
from tests.test_single_stage import SingleStageTester

tester = SingleStageTester()

# Test with different images
images = [
    "test_images/complete_markers.jpg",
    "test_images/missing_markers.jpg", 
    "test_images/no_markers.jpg"
]

for image_path in images:
    print(f"\nTesting: {image_path}")
    result = tester.test_stage('aruco_check', image_path)
    
    if result['success']:
        print(f"✅ Found {len(result['detected_markers'])} markers")
    else:
        print(f"❌ Failed: {result.get('error')}")
```

### Example 2: Testing OCR with Mock Data

```python
# Test roll number extraction with mock context
mock_context = {
    "rotated_image_path": "path/to/rotated_image.jpg",
    "detected_markers": [1, 2, 3, 4, 5]
}

result = tester.test_stage_with_mock_context(
    'roll_number_extraction', 
    'path/to/image.jpg', 
    mock_context
)

if result['success']:
    print(f"✅ Extracted roll number: {result['roll_number']}")
    print(f"📝 OCR text: {result['extracted_text']}")
```

### Example 3: Testing API Upload

```python
# Test API upload with complete mock data
mock_context = {
    "omr_data": {
        "roll_number": "123456",
        "detected_markers": [1, 2, 3, 4, 5],
        "omr_answers": {"q1": "A", "q2": "B"}
    }
}

result = tester.test_stage_with_mock_context(
    'api_upload',
    'path/to/image.jpg',
    mock_context
)

if result['success']:
    print(f"✅ Upload successful! ID: {result['upload_id']}")
```

## Creating Test Images

### Using the Built-in Test Image Creator

```bash
# Create a test image with ArUco markers
python tests/test_single_stage.py aruco_check test.jpg --create-test-image
```

### Creating Custom Test Images

```python
import cv2
import numpy as np

# Create a white image
image = np.ones((600, 800, 3), dtype=np.uint8) * 255

# Add text for OCR testing
cv2.putText(image, "Roll No: 123456", (50, 100), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Add OMR-style content
cv2.putText(image, "Question 1: A", (50, 150), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Save the image
cv2.imwrite("custom_test_image.jpg", image)
```

## Debugging Stages

### 1. **Enable Debug Output**

The stages include debug logging. Check the console output for detailed information about what each stage is doing.

### 2. **Check Context Data**

Use the interactive environment to inspect context data:

```bash
python tests/develop_stage.py
# Then select "Show current context"
```

### 3. **Test with Different Inputs**

Try different images and mock data to understand edge cases:

```python
# Test with empty context
result = tester.test_stage('roll_number_extraction', 'image.jpg', {})

# Test with minimal context
result = tester.test_stage('roll_number_extraction', 'image.jpg', 
                          {"rotated_image_path": "image.jpg"})

# Test with complete context
result = tester.test_stage('roll_number_extraction', 'image.jpg',
                          {"rotated_image_path": "image.jpg", "detected_markers": [1,2,3]})
```

### 4. **Handle Errors Gracefully**

Each stage should handle errors and return meaningful error messages:

```python
try:
    # Your stage logic here
    result = self.create_stage_result(success=True, data=processed_data)
except Exception as e:
    result = self.create_stage_result(
        success=False, 
        error=f"Stage failed: {str(e)}"
    )
```

## Planning Development Work

### 1. **Stage Dependency Analysis**

Understand which stages depend on others:

- **ArUco Check**: No dependencies
- **Orientation Check**: Depends on ArUco detection
- **Roll Number Extraction**: Depends on orientation (rotated image)
- **OMR Processing**: Depends on roll number and ArUco markers
- **API Upload**: Depends on OMR data

### 2. **Development Priority**

1. **Start with independent stages** (ArUco Check)
2. **Test with mock data** for dependent stages
3. **Test stage sequences** to verify data flow
4. **Test with real images** to validate functionality

### 3. **Testing Strategy**

```python
# Phase 1: Unit testing
tester.test_stage('aruco_check', 'test_image.jpg')

# Phase 2: Integration testing with mock data
tester.test_stage_with_mock_context('omr_processing', 'test_image.jpg', mock_data)

# Phase 3: End-to-end testing
tester.test_stage_sequence('test_image.jpg', ['aruco_check', 'orientation_check', 'roll_number_extraction'])

# Phase 4: Real-world testing
tester.test_stage_sequence('real_image.jpg', all_stages)
```

## Best Practices

### 1. **Always Test with Mock Data**

Don't rely on previous stages working correctly:

```python
# Good: Test with explicit mock data
mock_data = {"detected_markers": [1,2,3], "roll_number": "123456"}
result = tester.test_stage_with_mock_context('omr_processing', image_path, mock_data)

# Bad: Assume previous stages work
result = tester.test_stage_sequence(image_path, ['aruco_check', 'omr_processing'])
```

### 2. **Test Edge Cases**

```python
# Test with no markers
mock_data = {"detected_markers": []}
result = tester.test_stage_with_mock_context('omr_processing', image_path, mock_data)

# Test with missing roll number
mock_data = {"detected_markers": [1,2,3]}  # No roll_number
result = tester.test_stage_with_mock_context('omr_processing', image_path, mock_data)
```

### 3. **Use Consistent Test Images**

Create a set of test images with known characteristics:

- `test_no_markers.jpg` - No ArUco markers
- `test_few_markers.jpg` - Less than 5 markers
- `test_many_markers.jpg` - More than 5 markers
- `test_with_roll.jpg` - Contains roll number text
- `test_rotated.jpg` - Rotated image

### 4. **Document Your Tests**

Keep track of what you've tested:

```python
# Test log
test_cases = [
    {
        "stage": "aruco_check",
        "image": "test_no_markers.jpg",
        "expected": "fail",
        "actual": "fail",
        "notes": "Correctly detects no markers"
    },
    {
        "stage": "roll_number_extraction",
        "image": "test_with_roll.jpg",
        "mock_context": {"rotated_image_path": "test_with_roll.jpg"},
        "expected": "success",
        "actual": "success",
        "notes": "Extracts roll number correctly"
    }
]
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root
2. **Image Not Found**: Check file paths are correct
3. **Mock Context Errors**: Ensure JSON format is correct
4. **Stage Dependencies**: Use mock data for dependent stages

### Getting Help

1. **Check the examples**: `examples/stage_development_examples.py`
2. **Use interactive mode**: `python tests/develop_stage.py`
3. **Enable debug output**: Check console for detailed logs
4. **Test with simple cases**: Start with basic functionality

## Conclusion

Using these development tools, you can:

- **Develop stages independently** without running the full pipeline
- **Test thoroughly** with various inputs and edge cases
- **Debug effectively** with detailed logging and mock data
- **Plan development** systematically by understanding dependencies
- **Iterate quickly** with the interactive development environment

This approach makes stage development much more efficient and reliable! 🚀
