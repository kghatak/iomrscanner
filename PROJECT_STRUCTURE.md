# Project Structure

## Overview

This project has been reorganized into a clean, modular structure for better maintainability and organization. The new structure separates core functionality, tests, documentation, and examples into dedicated directories.

## Directory Structure

```
pyqt/
├── 📁 Core Application Files
│   ├── main.py                    # Main application entry point
│   ├── image_processor.py         # Core image processing functionality
│   ├── logger.py                  # Logging utilities
│   └── ui/                        # User interface components
│       ├── __init__.py
│       ├── main_window.py         # Main application window
│       ├── image_panel.py         # Image display panel
│       └── results_panel.py       # Results display panel
│
├── 📁 pipeline/                   # Modular pipeline system
│   ├── __init__.py               # Pipeline package initialization
│   └── pipeline_stages.py        # Pipeline stages and manager
│
├── 📁 tests/                      # Test suite
│   ├── __init__.py
│   ├── test_*.py                 # Main test files
│   ├── ut_*.py                   # Unit test files
│   └── create_test_image_with_roll.py
│
├── 📁 docs/                       # Documentation
│   ├── __init__.py
│   ├── MODULAR_PIPELINE_README.md # Modular pipeline documentation
│   ├── PIPELINE_README.md         # Original pipeline documentation
│   └── README_BATCH_PROCESSING.md # Batch processing guide
│
├── 📁 examples/                   # Example scripts and configurations
│   ├── __init__.py
│   ├── batch_processing_example.py # Batch processing example
│   ├── batch_config.json          # Batch processing configuration
│   └── omr_upload_server.py       # OMR upload server example
│
├── 📁 assets/                     # Static assets
│   └── README.md
│
├── 📁 Build and Configuration Files
│   ├── BUILD_GUIDE.md            # Build instructions
│   ├── INSTALLER_README.md       # Installer documentation
│   ├── check_dependencies.py     # Dependency checker
│   ├── build_*.py                # Build scripts
│   ├── build.sh                  # Build shell script
│   ├── Image Folder Analyzer.spec # PyInstaller spec
│   └── requirements.txt          # Python dependencies
│
└── 📁 Generated Directories (not in version control)
    ├── build/                     # Build artifacts
    ├── dist/                      # Distribution files
    ├── qt_env1/                   # Virtual environment
    └── __pycache__/              # Python cache files
```

## Key Changes

### 1. **Modular Pipeline System** (`pipeline/`)
- **`pipeline_stages.py`**: Contains all pipeline stage classes and the pipeline manager
- **`__init__.py`**: Makes the directory a proper Python package with clean imports

### 2. **Organized Test Suite** (`tests/`)
- All test files moved to dedicated directory
- Proper import paths configured for testing from subdirectory
- Includes both integration tests (`test_*.py`) and unit tests (`ut_*.py`)

### 3. **Comprehensive Documentation** (`docs/`)
- All documentation files centralized
- Separate guides for different aspects of the system
- Easy to find and maintain

### 4. **Example Code** (`examples/`)
- Example scripts and configurations
- Batch processing examples
- Server implementations

## Import Structure

### Core Application
```python
# Main application imports
from image_processor import ImageProcessor
from ui.main_window import MainWindow
```

### Pipeline System
```python
# Pipeline imports
from pipeline.pipeline_stages import PipelineManager, PipelineStage
from pipeline.pipeline_stages import ArUcoCheckStage, OrientationCheckStage
```

### Testing
```python
# Test file imports (from tests/ directory)
import sys
sys.path.append("..")  # Add parent directory to path
from image_processor import ImageProcessor
from pipeline.pipeline_stages import PipelineStage
```

## Running the Application

### Main Application
```bash
# From project root
python main.py
```

### Tests
```bash
# Run all tests
cd tests
python -m pytest

# Run specific test
python test_modular_pipeline.py
```

### Examples
```bash
# Run batch processing example
cd examples
python batch_processing_example.py
```

## Development Workflow

### 1. **Adding New Pipeline Stages**
```python
# Create new stage in pipeline/pipeline_stages.py
class MyCustomStage(PipelineStage):
    def get_stage_name(self) -> str:
        return "my_custom_stage"
    
    def process(self, image_path: str, context: dict) -> dict:
        # Your processing logic
        return self.create_stage_result(success=True)
```

### 2. **Adding New Tests**
```python
# Create test file in tests/
import sys
sys.path.append("..")
from image_processor import ImageProcessor

def test_my_feature():
    processor = ImageProcessor()
    # Your test logic
```

### 3. **Adding Documentation**
- Add documentation files to `docs/`
- Update this `PROJECT_STRUCTURE.md` if needed
- Keep documentation close to related code

### 4. **Adding Examples**
- Place example scripts in `examples/`
- Include configuration files as needed
- Document usage in README files

## Benefits of New Structure

### 1. **Maintainability**
- Clear separation of concerns
- Easy to locate specific functionality
- Modular design reduces coupling

### 2. **Testability**
- Dedicated test directory
- Proper import paths
- Easy to run specific test suites

### 3. **Documentation**
- Centralized documentation
- Easy to find relevant guides
- Separate documentation for different features

### 4. **Extensibility**
- Easy to add new pipeline stages
- Clear structure for new features
- Modular design supports growth

### 5. **Deployment**
- Clear separation of source and build files
- Easy to package for distribution
- Clean structure for CI/CD

## Migration Notes

### For Existing Code
- All existing functionality preserved
- Import paths updated automatically
- No breaking changes to API

### For New Development
- Use the new directory structure
- Follow the established patterns
- Add tests in the `tests/` directory
- Document new features in `docs/`

## File Naming Conventions

- **Core files**: `snake_case.py`
- **Test files**: `test_*.py` (integration), `ut_*.py` (unit)
- **Documentation**: `*.md`
- **Configuration**: `*.json`, `*.yaml`
- **Build files**: `build_*.py`, `*.spec`

This structure provides a clean, organized foundation for the image processing pipeline system while maintaining all existing functionality and making future development much easier.
