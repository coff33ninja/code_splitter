# Python Code Splitter

A powerful tool for splitting large Python files into modular, maintainable components while preserving full backward compatibility.

## 🚀 Overview

The Python Code Splitter transforms monolithic Python files into organized, modular structures. It automatically:

- **Backs up** your original file safely
- **Splits classes** into individual, focused modules
- **Creates an interface file** that maintains all existing imports
- **Validates** the split code to ensure everything works correctly
- **Preserves** all functionality while improving maintainability

## 📁 What It Does

### Before: Monolithic File

```
sample_large_file.py         # 400+ lines, 10 classes, multiple responsibilities
```

### After: Modular Structure

```
sample_large_file.py.backup  # ← Safe backup of original
demo_output/
├── sample_large_file.py     # ← Clean interface file (maintains compatibility)
└── sample_large_file/       # ← Organized modules
    ├── __init__.py
    ├── UserProfile.py       # ← Single responsibility
    ├── DataRecord.py        # ← Focused functionality
    ├── DatabaseConnection.py # ← Easy to maintain
    ├── APIClient.py
    ├── DataProcessor.py
    └── ... (10 total modules)
```

## 🛠️ Installation & Usage

### Basic Usage

```bash
# Split a Python file
python cli.py -i your_file.py -o output_directory

# With documentation generation
python cli.py -i your_file.py -o output_directory --doc

# With custom configuration
python cli.py -i your_file.py -o output_directory --config config.json
```

### Example with Sample File

```bash
# Split the sample large file
python cli.py -i sample_large_file.py -o demo_output
```

**Output:**

```
📦 Created backup: sample_large_file.py.backup
📄 Created interface file: demo_output\sample_large_file.py

🔍 Running post-split validation...
📝 Syntax validation: 12/12 files passed
📦 Import validation: 10/12 files imported successfully
🏗️ Functionality validation: 10/10 classes available (0 missing)

✅ Splitting complete and validated! Files in demo_output
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

### 3. **Dependency Management**

- Automatically handles imports between split modules
- Preserves external library imports
- Creates proper relative import structure

### 4. **Interface File Generation**

- Creates a new file at the original location
- Imports all classes from split modules
- Maintains 100% backward compatibility

### 5. **Comprehensive Validation**

- **Syntax validation**: Ensures all files are syntactically correct
- **Import validation**: Tests that modules can be imported
- **Functionality validation**: Verifies all classes are accessible

## 📊 Real-World Example: Sample Application

### Original File Stats

- **File**: `sample_large_file.py`
- **Size**: 400+ lines
- **Classes**: 10 comprehensive classes
- **Complexity**: Multiple responsibilities, tightly coupled

### After Splitting

- **Backup**: `sample_large_file.py.backup` (safe copy)
- **Interface**: `demo_output/sample_large_file.py` (clean API)
- **Modules**: 12 focused files in `demo_output/sample_large_file/`

### Split Modules Created

```
UserProfile.py              # User data management
DataRecord.py               # Data record handling
DatabaseConnection.py       # Database operations
APIClient.py                # External API communication
DataProcessor.py            # Data processing logic
CacheManager.py             # Caching functionality
ConfigurationManager.py     # Configuration handling
EventLogger.py              # Event logging system
ApplicationManager.py       # Main application coordination
functions.py                # Utility functions
... and more focused modules
```

## 🔄 Backward Compatibility

### Before Splitting

```python
# Your existing code works exactly the same
from sample_large_file import UserProfile, DataRecord
from sample_large_file import ApplicationManager

user = UserProfile("123", "john_doe", "john@example.com", datetime.now())
app = ApplicationManager()
```

### After Splitting

```python
# Same imports still work! No code changes needed
from sample_large_file import UserProfile, DataRecord
from sample_large_file import ApplicationManager

user = UserProfile("123", "john_doe", "john@example.com", datetime.now())
app = ApplicationManager()
```

The interface file (`demo_output/sample_large_file.py`) handles all the complexity:

```python
"""Interface module for sample_large_file."""

from .sample_large_file.UserProfile import UserProfile
from .sample_large_file.DataRecord import DataRecord
from .sample_large_file.ApplicationManager import ApplicationManager
# ... imports for all 10 classes

__all__ = [
    "UserProfile",
    "DataRecord",
    "ApplicationManager",
    # ... all 10 classes
]
```

## 🏗️ Advanced Configuration

### Custom Module Grouping

Create a `config.json` to group related classes:

```json
{
  "modules": {
    "data_models": {
      "classes": ["UserProfile", "DataRecord"],
      "functions": []
    },
    "services": {
      "classes": ["DatabaseConnection", "APIClient"],
      "functions": ["validate_email", "generate_id"]
    }
  }
}
```

### Documentation Generation

```bash
python cli.py -i sample_large_file.py -o output --doc
```

Generates comprehensive documentation for all split modules.

## 📈 Benefits

### For Developers

- **Easier Navigation**: Find specific functionality quickly
- **Focused Development**: Work on single-responsibility modules
- **Better Testing**: Test individual components in isolation
- **Cleaner Git Diffs**: Changes affect only relevant files

### For Teams

- **Reduced Conflicts**: Multiple developers can work on different modules
- **Code Reviews**: Smaller, focused files are easier to review
- **Onboarding**: New team members can understand components individually

### For Maintenance

- **Debugging**: Issues isolated to specific modules
- **Refactoring**: Modify individual classes without affecting others
- **Documentation**: Each module can have focused documentation

## 🔍 Validation & Quality Assurance

The splitter includes comprehensive validation:

### Syntax Validation

- Parses all generated files for syntax errors
- Reports any malformed code
- Ensures clean, valid Python

### Import Validation

- Tests that all modules can be imported
- Identifies missing dependencies
- Validates relative import structure

### Functionality Validation

- Compares original vs split functionality
- Ensures no classes or functions are lost
- Validates that all components are accessible

## 🚦 Getting Started

1. **Clone or download** the splitter
2. **Try with the sample file**:
   ```bash
   python cli.py -i sample_large_file.py -o demo_output
   ```
3. **Review the results**:
   - Check the backup file was created
   - Examine the split modules
   - Test the interface file
4. **Use with your own files**:
   ```bash
   python cli.py -i your_large_file.py -o output_folder
   ```
5. **Update your imports** (if needed) or enjoy seamless compatibility!

## 📝 Example Output

```
📦 Created backup: sample_large_file.py.backup
⚠️ Black not found. Skipping code formatting.
📄 Created interface file: demo_output\sample_large_file.py

🔍 Running post-split validation...
🔍 Running syntax validation...
🔍 Running import validation...
🔍 Running functionality comparison...

📝 Syntax validation: 12/12 files passed
📦 Import validation: 10/12 files imported successfully
🏗️ Functionality validation: 10/10 classes available (0 missing)

✅ Splitting complete and validated! Files in demo_output
```

## 🤝 Contributing

This tool was designed to handle real-world, complex Python files. If you encounter issues with specific file structures or have suggestions for improvements, contributions are welcome!

## 📄 License

Open source - feel free to use, modify, and distribute.

---

**Transform your monolithic Python files into maintainable, modular code while preserving full backward compatibility!**
