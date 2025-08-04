# Python Code Splitter

A powerful tool for splitting large Python files into modular, maintainable components while preserving full backward compatibility.

## 🚀 Overview

The Python Code Splitter transforms monolithic Python files into organized, modular structures. It automatically:

- **Backs up** your original file safely
- **Splits classes** into individual, focused modules
- **Creates an interface file** that maintains all existing imports
- **Validates** the split code with comprehensive quality checks
- **Handles main blocks** flexibly based on your needs
- **Optimizes imports** and removes unused dependencies
- **Preserves** all functionality while improving maintainability

## 📁 What It Does

### Before: Monolithic File

```
sample_large_file.py           # 500+ lines, multiple classes, mixed responsibilities
```

### After: Modular Structure

```
sample_large_file.py.backup    # ← Safe backup of original
output/
├── sample_large_file.py       # ← Clean interface file (maintains compatibility)
└── sample_large_file/         # ← Organized modules
    ├── __init__.py
    ├── _internal_imports.py # ← Internal dependencies and imports
    ├── main.py              # ← Main execution logic (configurable)
    ├── ClassOne.py          # ← Single responsibility
    ├── ClassTwo.py          # ← Focused functionality
    ├── ClassThree.py        # ← Easy to maintain
    ├── functions.py         # ← Utility functions
    └── ... (focused modules)
```

## 🛠️ Installation & Setup

### Core Files

Download these essential files:

- `cli.py` - Command line interface
- `splitter_core.py` - Core splitting logic
- `docgen.py` - Documentation generation

### Optional Dependencies (Recommended)

For the best experience, install these optional tools:

```bash
pip install black pyflakes
```

- **black**: Automatic code formatting for clean, consistent output
- **pyflakes**: Unused import detection and validation

## 🎯 Usage

### Basic Command

```bash
python cli.py -i sample_large_file.py -o output_directory
```

### Advanced Options

```bash
# With documentation generation
python cli.py -i sample_large_file.py -o output --doc

# With custom configuration
python cli.py -i sample_large_file.py -o output --config config.json

# Keep main block in interface file
python cli.py -i sample_large_file.py -o output --main-handling keep

# Remove main block entirely
python cli.py -i sample_large_file.py -o output --main-handling discard
```

### CLI Options

| Option            | Description                                     | Default    |
| ----------------- | ----------------------------------------------- | ---------- |
| `-i, --input`     | Path to Python file to split (required)         | -          |
| `-o, --output`    | Output directory for split files                | `"output"` |
| `--doc`           | Generate documentation for split modules        | `False`    |
| `--config`        | Path to JSON configuration file                 | `None`     |
| `--main-handling` | How to handle `if __name__ == '__main__'` block | `"move"`   |

### Main Block Handling Options

- **`move`** (default): Creates separate `main.py` file - best for modular applications
- **`keep`**: Keeps main block in interface file - interface remains executable
- **`discard`**: Removes main block entirely - perfect for library modules

## 📊 Example Output

```
📦 Created backup: your_file.py.backup
📄 Created interface file: output\your_file.py

🔍 Running post-split validation...
🔍 Running syntax validation...
🔍 Running import validation...
🔍 Running functionality comparison...
🔍 Running unused import validation...

✅ All validation tests passed! Split files are working correctly.

📝 Syntax validation: 15/15 files passed
📦 Import validation: 14/15 files imported successfully
🏗️ Functionality validation: 12/12 classes available (0 missing)
✅ Unused import validation: All imports are used

✅ Splitting complete and validated! Files in output
```

## 🎯 Key Features

### 1. **Safe Backup System**

- Original file automatically backed up as `.backup`
- Never lose your original code
- Easy rollback if needed

### 2. **Intelligent Class Extraction**

- Each class becomes its own module
- Preserves all methods, properties, and docstrings
- Maintains inheritance and decorators
- Smart dependency analysis for clean imports

### 3. **Flexible Main Block Handling**

- **Move**: Separate `main.py` for clean modular structure
- **Keep**: Executable interface file for simple deployment
- **Discard**: Library-ready modules without execution code

### 4. **Advanced Import Management**

- Automatically handles imports between split modules
- Preserves external library imports
- Creates proper relative import structure
- Detects and reports unused imports

### 5. **Interface File Generation**

- Creates a new file at the original location
- Imports all classes from split modules
- Maintains 100% backward compatibility
- Clean, documented interface

### 6. **Comprehensive Validation Pipeline**

- **Syntax validation**: Ensures all files are syntactically correct
- **Import validation**: Tests that modules can be imported
- **Functionality validation**: Verifies all classes are accessible
- **Unused import validation**: Identifies and reports unused imports

## 🔄 Backward Compatibility

### Your Existing Code Still Works

```python
# All these imports continue to work exactly as before:
from your_module import ClassOne, ClassTwo
from your_module import SomeFunction
import your_module

# Create instances exactly as before:
obj = ClassOne()
result = SomeFunction()
```

### New Modular Options Available

```python
# Now you can also import directly from modules:
from your_module.ClassOne import ClassOne
from your_module.functions import SomeFunction

# Or work with individual modules:
import your_module.ClassOne as c1
import your_module.ClassTwo as c2
```

### Interface File Magic

The generated interface file (`output/your_module.py`) handles all complexity:

```python
"""
Interface module for your_module.

This file provides a clean interface to all classes and functions
that were split into separate modules. Import from this file
to maintain compatibility with existing code.
"""

from .your_module.ClassOne import ClassOne
from .your_module.ClassTwo import ClassTwo
from .your_module.functions import SomeFunction
# ... imports for all classes and functions

__all__ = [
    "ClassOne",
    "ClassTwo",
    "SomeFunction",
    # ... all exports
]
```

## 🏗️ Advanced Configuration

### Custom Module Grouping

Create a `config.json` to group related classes:

```json
{
  "modules": {
    "data_models": {
      "classes": ["User", "Profile", "Settings"],
      "functions": []
    },
    "services": {
      "classes": ["DatabaseService", "APIService"],
      "functions": ["validate_data", "format_response"]
    },
    "utilities": {
      "classes": [],
      "functions": ["helper_function", "utility_method"]
    }
  }
}
```

### Documentation Generation

```bash
python cli.py -i sample_large_file.py -o output --doc
```

Generates comprehensive documentation for all split modules with:

- Class documentation
- Method signatures
- Usage examples
- Cross-references between modules

## 📈 Benefits

### For Developers

- **Easier Navigation**: Find specific functionality quickly
- **Focused Development**: Work on single-responsibility modules
- **Better Testing**: Test individual components in isolation
- **Cleaner Code**: Unused import detection keeps modules lean
- **Flexible Structure**: Choose how to handle main execution blocks

### For Teams

- **Reduced Conflicts**: Multiple developers can work on different modules
- **Code Reviews**: Smaller, focused files are easier to review
- **Onboarding**: New team members can understand components individually
- **Consistent Style**: Black formatting ensures uniform code appearance

### For Maintenance

- **Debugging**: Issues isolated to specific modules
- **Refactoring**: Modify individual classes without affecting others
- **Documentation**: Each module can have focused documentation
- **Quality Assurance**: Comprehensive validation catches issues early

## 🔍 Quality Assurance & Validation

### 4-Step Validation Pipeline

#### 1. Syntax Validation

- Parses all generated files for syntax errors
- Reports any malformed code
- Ensures clean, valid Python

#### 2. Import Validation

- Tests that all modules can be imported
- Identifies missing dependencies
- Validates relative import structure

#### 3. Functionality Validation

- Compares original vs split functionality
- Ensures no classes or functions are lost
- Validates that all components are accessible

#### 4. Unused Import Validation (NEW!)

- Uses `pyflakes` to detect unused imports
- Reports unnecessary dependencies
- Helps keep modules clean and optimized

### Graceful Fallbacks

- Works without optional dependencies
- Clear warnings when tools are missing
- Continues processing with available features

## 🚀 Use Cases

### 1. **Library Development** (`--main-handling discard`)

```bash
python cli.py -i my_library.py -o lib_output --main-handling discard
```

Perfect for modules that will be imported by other code. Removes execution logic for clean library structure.

### 2. **Application Refactoring** (`--main-handling keep`)

```bash
python cli.py -i my_app.py -o app_output --main-handling keep
```

Interface file remains executable while classes are modularized. Great for gradual refactoring.

### 3. **Modular Architecture** (`--main-handling move` - default)

```bash
python cli.py -i my_app.py -o app_output --main-handling move
```

Clean separation with dedicated `main.py` for execution logic. Best for new modular applications.

## 🚦 Getting Started

### Quick Start

1. **Download the splitter files**
2. **Run on your file**:
   ```bash
   python cli.py -i your_large_file.py -o output
   ```
3. **Review results**:
   - ✅ Backup created: `your_large_file.py.backup`
   - ✅ Split modules in: `output/your_large_file/`
   - ✅ Interface file: `output/your_large_file.py`
4. **Start using immediately** - all existing imports still work!

### Best Practices

- Install `black` and `pyflakes` for optimal results
- Use `--main-handling` appropriate for your use case
- Review the validation output for any warnings
- Test your existing code with the new modular structure

## 📝 Real-World Example

### Input File: `sample_large_file.py` (400+ lines)

```python
# Large file with multiple classes and responsibilities
class UserProfile: ...
class DatabaseConnection: ...
class APIClient: ...
class DataProcessor: ...
# ... 6 more classes
# ... utility functions
# ... main execution block
```

### Command

```bash
python cli.py -i sample_large_file.py -o demo_output
```

### Generated Structure

```
demo_output/
├── sample_large_file.py          # Interface file
└── sample_large_file/
    ├── __init__.py               # Package initialization
    ├── _internal_imports.py      # Internal dependencies
    ├── main.py                   # Main execution logic
    ├── UserProfile.py            # User management
    ├── DatabaseConnection.py     # Database operations
    ├── APIClient.py              # API communication
    ├── DataProcessor.py          # Data processing
    ├── CacheManager.py           # Caching functionality
    ├── ConfigurationManager.py   # Configuration handling
    ├── EventLogger.py            # Event logging
    ├── ApplicationManager.py     # Application coordination
    └── functions.py              # Utility functions
```

### Validation Results

```
✅ All validation tests passed! Split files are working correctly.
📝 Syntax validation: 13/13 files passed
📦 Import validation: 12/13 files imported successfully
🏗️ Functionality validation: 9/9 classes available (0 missing)
✅ Unused import validation: All imports are used
```

## 🤝 Contributing

This tool handles real-world, complex Python files. Contributions welcome for:

- Additional validation checks
- New configuration options
- Enhanced import analysis
- Documentation improvements

## 📄 License

Open source - feel free to use, modify, and distribute.

---

**Transform your monolithic Python files into maintainable, modular architectures with intelligent import handling, flexible main block management, and comprehensive quality assurance!** 🚀
