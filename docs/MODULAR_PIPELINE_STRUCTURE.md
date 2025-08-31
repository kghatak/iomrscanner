# Modular Pipeline Structure

## Overview

The pipeline has been refactored into a modular, class-based system where each stage is implemented in its own file. This provides better organization, maintainability, and extensibility.

## File Structure

```
pipeline/
├── __init__.py                    # Package initialization
├── base_stage.py                  # Abstract base class for all stages
├── pipeline_stages.py             # Pipeline manager and orchestration
├── aruco_check_stage.py           # Stage 1: ArUco marker detection
├── orientation_check_stage.py     # Stage 2: Image orientation and rotation
├── roll_number_extraction_stage.py # Stage 3: OCR for roll number extraction
├── omr_processing_stage.py        # Stage 4: OMR sheet processing
└── api_upload_stage.py            # Stage 5: API data upload
```

## Key Components

### 1. Base Stage Class (`base_stage.py`)

**Purpose**: Abstract base class that all pipeline stages inherit from.

**Key Methods**:
- `process()`: Abstract method for stage processing logic
- `get_stage_name()`: Abstract method for stage identifier
- `get_stage_description()`: Abstract method for human-readable description
- `create_stage_result()`: Helper method for standardized results
- `handle_pipeline_error()`: Error handling and image marking
- `mark_image_as_error()`: Visual error marking with red lines

### 2. Pipeline Manager (`pipeline_stages.py`)

**Purpose**: Orchestrates the pipeline flow and manages stage execution.

**Key Methods**:
- `process_image()`: Main pipeline execution
- `add_stage()`: Add new stages to pipeline
- `remove_stage()`: Remove stages from pipeline
- `get_stage()`: Retrieve specific stage by name
- `get_stages_info()`: Get information about all stages

### 3. Individual Stage Files

Each stage is implemented in its own file, making it easy to:
- **Modify** individual stages without affecting others
- **Add** new stages by creating new files
- **Remove** stages by deleting files and updating imports
- **Test** stages independently
- **Maintain** clear separation of concerns

## Stage Implementations

### Stage 1: ArUco Check (`aruco_check_stage.py`)
- **Purpose**: Verify ArUco markers are present
- **Requirements**: Minimum 5 markers detected
- **Output**: List of detected marker IDs

### Stage 2: Orientation Check (`orientation_check_stage.py`)
- **Purpose**: Check image orientation and rotate if needed
- **Logic**: Uses ArUco marker positions to determine rotation
- **Output**: Rotated image path (if rotation applied)

### Stage 3: Roll Number Extraction (`roll_number_extraction_stage.py`)
- **Purpose**: Extract exam roll number using OCR
- **Dependencies**: pytesseract
- **Output**: Extracted roll number and OCR text

### Stage 4: OMR Processing (`omr_processing_stage.py`)
- **Purpose**: Process OMR sheet and extract answers
- **Logic**: Placeholder for actual OMR processing
- **Output**: OMR data with answers

### Stage 5: API Upload (`api_upload_stage.py`)
- **Purpose**: Upload processed data to API
- **Logic**: Simulated API upload
- **Output**: Upload confirmation and ID

## Benefits of Modular Structure

### 1. **Maintainability**
- Each stage is isolated in its own file
- Changes to one stage don't affect others
- Clear separation of concerns

### 2. **Extensibility**
- Easy to add new stages by creating new files
- Simple to remove stages by deleting files
- Flexible stage ordering

### 3. **Testability**
- Each stage can be tested independently
- Mock stages can be created for testing
- Unit tests for individual stages

### 4. **Readability**
- Smaller, focused files
- Clear file names indicate purpose
- Easier to understand and navigate

### 5. **Reusability**
- Stages can be reused in different pipelines
- Base class provides common functionality
- Consistent interface across all stages

## Adding New Stages

To add a new stage:

1. **Create a new file** in the `pipeline/` directory
2. **Import the base class**: `from .base_stage import PipelineStage`
3. **Implement the required methods**:
   ```python
   class MyNewStage(PipelineStage):
       def get_stage_name(self) -> str:
           return "my_new_stage"
       
       def get_stage_description(self) -> str:
           return "Description of what this stage does"
       
       def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
           # Your processing logic here
           return self.create_stage_result(success=True, data=result)
   ```
4. **Add import** to `pipeline_stages.py`:
   ```python
   from .my_new_stage import MyNewStage
   ```
5. **Add to default stages** in `PipelineManager._initialize_default_stages()`:
   ```python
   self.stages = [
       # ... existing stages ...
       MyNewStage(self.processor)
   ]
   ```

## Removing Stages

To remove a stage:

1. **Delete the stage file** (e.g., `my_stage.py`)
2. **Remove the import** from `pipeline_stages.py`
3. **Remove from default stages** in `PipelineManager._initialize_default_stages()`

## Context Flow

The `context` dictionary flows through all stages:

```python
# Stage 1 adds data
context = {
    "original_image_path": "/path/to/image.jpg",
    "current_image_path": "/path/to/image.jpg",
    "detected_markers": [1, 2, 3, 4, 5]  # Added by Stage 1
}

# Stage 2 uses and adds data
context = {
    "original_image_path": "/path/to/image.jpg",
    "current_image_path": "/path/to/rotated_image.jpg",  # Updated
    "detected_markers": [1, 2, 3, 4, 5],
    "rotation_applied": 90  # Added by Stage 2
}

# And so on...
```

## Error Handling

Each stage inherits error handling methods from the base class:

- **Automatic error detection**: Failed stages trigger error handling
- **Visual error marking**: Red lines added to failed images
- **Error folder organization**: Failed images moved to error folder
- **Pipeline continuation**: Processing continues with next image

## Testing the Modular Structure

```python
# Test individual stage
from pipeline.aruco_check_stage import ArUcoCheckStage
stage = ArUcoCheckStage(processor)
result = stage.process(image_path, context)

# Test pipeline manager
from pipeline.pipeline_stages import PipelineManager
manager = PipelineManager(processor)
result = manager.process_image(image_path, output_folder)

# Test adding custom stage
class CustomStage(PipelineStage):
    # Implementation...
    pass

manager.add_stage(CustomStage(processor))
```

## Migration from Monolithic Structure

The refactoring maintains full backward compatibility:

- **Same API**: `ImageProcessor.process_image_pipeline()` works unchanged
- **Same functionality**: All stages work exactly as before
- **Same error handling**: Error marking and folder organization unchanged
- **Same context flow**: Data flows between stages identically

The only difference is improved organization and maintainability!
