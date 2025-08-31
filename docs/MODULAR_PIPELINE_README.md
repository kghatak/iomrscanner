# Modular Pipeline System

## Overview

The modular pipeline system provides a flexible, extensible approach to image processing with the ability to add, remove, and modify processing stages dynamically. Each stage is implemented as a separate class that inherits from a common base class, making the system highly maintainable and customizable.

## Architecture

### Core Components

1. **`PipelineStage` (Abstract Base Class)**
   - Defines the interface for all pipeline stages
   - Provides common functionality and result formatting
   - Ensures consistent behavior across all stages

2. **`PipelineManager`**
   - Manages the collection of pipeline stages
   - Orchestrates the processing flow
   - Handles stage execution and error propagation

3. **Individual Stage Classes**
   - Each stage inherits from `PipelineStage`
   - Implements specific processing logic
   - Can be easily added, removed, or modified

## Stage Classes

### Built-in Stages

#### 1. `ArUcoCheckStage`
- **Purpose**: Check if basic ArUco markers are present
- **Input**: Image path
- **Output**: Detected marker IDs and detection info
- **Failure**: Insufficient markers found

#### 2. `OrientationCheckStage`
- **Purpose**: Check image orientation and rotate if needed
- **Input**: Image path
- **Output**: Rotated image path and rotation angle
- **Failure**: No markers found for orientation detection

#### 3. `RollNumberExtractionStage`
- **Purpose**: Extract exam roll number using OCR
- **Input**: Image path (preferably rotated)
- **Output**: Extracted roll number and OCR text
- **Failure**: No valid roll number found

#### 4. `OMRProcessingStage`
- **Purpose**: Process the OMR sheet
- **Input**: Image path and roll number
- **Output**: OMR data with answers
- **Failure**: OMR processing errors

#### 5. `APIUploadStage`
- **Purpose**: Upload processed data to API
- **Input**: OMR data and roll number
- **Output**: Upload ID and API response
- **Failure**: API upload errors

## Creating Custom Stages

### Step 1: Define Your Stage Class

```python
from pipeline_stages import PipelineStage

class MyCustomStage(PipelineStage):
    """Custom stage for specific processing"""
    
    def get_stage_name(self) -> str:
        return "my_custom_stage"
    
    def get_stage_description(self) -> str:
        return "My custom processing stage"
    
    def process(self, image_path: str, context: dict) -> dict:
        try:
            # Your processing logic here
            # Access previous stage results from context
            
            # Example: Get data from previous stage
            previous_data = context.get('some_previous_data', None)
            
            # Your processing...
            result = self.do_my_processing(image_path, previous_data)
            
            if result.success:
                return self.create_stage_result(
                    success=True,
                    processed_data=result.data,
                    additional_info=result.info
                )
            else:
                return self.create_stage_result(
                    success=False,
                    error=result.error_message
                )
                
        except Exception as e:
            return self.create_stage_result(
                success=False,
                error=f"Custom stage failed: {str(e)}"
            )
```

### Step 2: Add Your Stage to the Pipeline

```python
from image_processor import ImageProcessor

# Initialize processor
processor = ImageProcessor()

# Create your custom stage
custom_stage = MyCustomStage(processor)

# Add to pipeline (at the end by default)
processor.add_pipeline_stage(custom_stage)

# Or add at specific position
processor.add_pipeline_stage(custom_stage, position=2)  # After stage 2
```

## Pipeline Management

### Adding Stages

```python
# Add stage at the end
processor.add_pipeline_stage(my_stage)

# Add stage at specific position
processor.add_pipeline_stage(my_stage, position=1)
```

### Removing Stages

```python
# Remove stage by name
success = processor.remove_pipeline_stage("stage_name")
```

### Getting Stage Information

```python
# Get all stage information
stages_info = processor.get_pipeline_stages_info()
for stage_info in stages_info:
    print(f"{stage_info['name']}: {stage_info['description']}")

# Get specific stage
stage = processor.get_pipeline_stage("stage_name")
```

## Example Use Cases

### 1. Quality Control Pipeline

```python
# Create quality-focused pipeline
processor = ImageProcessor()

# Remove default stages
processor.remove_pipeline_stage("api_upload")
processor.remove_pipeline_stage("omr_processing")

# Add quality check stage
quality_stage = ImageQualityCheckStage(processor)
processor.add_pipeline_stage(quality_stage, position=1)
```

### 2. Minimal Processing Pipeline

```python
# Create minimal pipeline
processor = ImageProcessor()

# Remove all stages
for stage in processor.get_pipeline_stages_info():
    processor.remove_pipeline_stage(stage['name'])

# Add only essential stages
processor.add_pipeline_stage(ArUcoCheckStage(processor))
processor.add_pipeline_stage(RollNumberExtractionStage(processor))
```

## Best Practices

### 1. Stage Design
- Keep stages focused on a single responsibility
- Use descriptive stage names and descriptions
- Handle errors gracefully with meaningful messages
- Document any dependencies on previous stages

### 2. Error Handling
- Always use try-catch blocks
- Return standardized error results
- Provide specific, actionable error messages

### 3. Testing
- Test each stage independently
- Test stage integration
- Test error scenarios
- Test with various input types

## Migration from Old System

The old pipeline system used individual methods in the `ImageProcessor` class. The new modular system provides the same functionality but with better organization:

### Old System
```python
# Old way
result = processor._stage1_check_aruco_markers(image_path)
result = processor._stage2_check_and_rotate_image(image_path)
# ... etc
```

### New System
```python
# New way
result = processor.process_image_pipeline(image_path, output_folder)
# Stages are managed automatically by PipelineManager
```

The new system maintains backward compatibility while providing much more flexibility and maintainability.
