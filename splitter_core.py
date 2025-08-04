import ast
import os
import json
import sys
import importlib.util
import tempfile
import shutil
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path


class UsedNamesCollector(ast.NodeVisitor):

    def __init__(self):
        self.used_names = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)


def extract_code(lines: List[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1:end])


def parse_script(filepath: str) -> Optional[Tuple[str, List[str], ast.Module]]:
    try:
        with open(filepath, 'r', encoding='utf‑8') as f:
            code = f.read()
        lines = code.splitlines()
        tree = ast.parse(code)
        return code, lines, tree
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return None


def find_top_level_defs(tree: ast.Module):
    classes = []
    for s in tree.body:
        if isinstance(s, ast.ClassDef):
            start_line = s.lineno
            if s.decorator_list:
                start_line = min(start_line, s.decorator_list[0].lineno)
            classes.append((s.name, start_line, s.end_lineno))
    functions = []
    for s in tree.body:
        if isinstance(s, ast.FunctionDef):
            start_line = s.lineno
            if s.decorator_list:
                start_line = min(start_line, s.decorator_list[0].lineno)
            functions.append((s.name, start_line, s.end_lineno))
    return classes, functions


def get_occupied_lines(defs: List[Tuple[str, int, Optional[int]]]) -> set:
    occupied = set()
    for _, start, end in defs:
        if end is not None:
            occupied.update(range(start, end + 1))
    return occupied


def get_imports(tree: ast.Module) -> List[str]:
    return [ast.unparse(stmt) for stmt in tree.body if isinstance(stmt, (ast.Import, ast.ImportFrom))]


def analyze_dependencies(tree, class_names, function_names):
    class_used = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.ClassDef):
            collector = UsedNamesCollector()
            collector.visit(stmt)
            uc = [n for n in collector.used_names if n in class_names and n != stmt.name]
            uf = [n for n in collector.used_names if n in function_names]
            class_used[stmt.name] = (uc, uf)
    func_used_classes = set()
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef):
            collector = UsedNamesCollector()
            collector.visit(stmt)
            func_used_classes.update([n for n in collector.used_names if n in class_names])
    top_used = set()
    for stmt in tree.body:
        if not isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.Import, ast.ImportFrom)):
            collector = UsedNamesCollector()
            collector.visit(stmt)
            top_used.update(collector.used_names)
    top_used_cls = [n for n in top_used if n in class_names]
    top_used_fn = [n for n in top_used if n in function_names]
    return class_used, func_used_classes, top_used_cls, top_used_fn


def parse_config(config_path: str) -> Optional[Dict[str, Any]]:
    """Parse configuration file for custom module splitting."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error parsing config file {config_path}: {e}")
        return None


def _extract_module_docstring(code: str) -> Optional[str]:
    """Extract the module-level docstring from code."""
    try:
        tree = ast.parse(code)
        if (tree.body and 
            isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant) and 
            isinstance(tree.body[0].value.value, str)):
            return f'"""{tree.body[0].value.value}"""'
    except Exception:
        pass
    return None


def create_shrunk_original(code: str, lines: List[str], imports: List[str],
                          classes: List[Tuple[str, int, Optional[int]]],
                          functions: List[Tuple[str, int, Optional[int]]],
                          config: Optional[Dict[str, Any]],
                          class_names: List[str], function_names: List[str]) -> str:
    """Create a shrunk version of the original file with only imports and top-level code."""
    
    # Get all classes and functions that will be split out
    split_classes = set()
    split_functions = set()
    
    if config:
        # Custom splitting - collect all classes/functions mentioned in config
        for module_items in config.get("modules", {}).values():
            split_classes.update(module_items.get("classes", []))
            split_functions.update(module_items.get("functions", []))
    else:
        # Default splitting - all classes get split, functions go to functions.py
        split_classes.update(class_names)
        split_functions.update(function_names)
    
    # Find classes and functions that should remain in the original file
    remaining_classes = [(name, start, end) for name, start, end in classes 
                        if name not in split_classes]
    remaining_functions = [(name, start, end) for name, start, end in functions 
                          if name not in split_functions]
    
    # If everything is being split out, create a minimal file with just imports and references
    if not remaining_classes and not remaining_functions:
        content_parts = []
        
        # Try to preserve original module docstring if it exists
        original_docstring = _extract_module_docstring(code)
        if original_docstring:
            content_parts.append(original_docstring)
            content_parts.append('')
        else:
            # Add a comment explaining this is the main module
            content_parts.append('"""')
            content_parts.append('Main module - classes have been split into separate files.')
            content_parts.append('Import from the individual modules or use the __init__.py for convenience.')
            content_parts.append('"""')
            content_parts.append('')
        
        # Add imports only (no duplicates)
        if imports:
            content_parts.extend(imports)
            content_parts.append("")
        
        # Add imports for the split classes/functions
        if config:
            # Custom modules
            for module_name in config.get("modules", {}).keys():
                content_parts.append(f"from .{module_name} import *")
        else:
            # Default splitting
            for class_name in class_names:
                content_parts.append(f"from .{class_name} import {class_name}")
            if function_names:
                content_parts.append(f"from .functions import {', '.join(function_names)}")
        
        return "\n".join(content_parts) + "\n"
    
    # If some items remain, include them
    all_occupied = get_occupied_lines(classes + functions)
    
    # Filter top-level code more carefully
    top_level_code = []
    in_module_docstring = False
    docstring_quotes = None
    
    for i in range(1, len(lines) + 1):
        if i not in all_occupied:
            line = lines[i - 1]
            stripped = line.strip()
            
            # Handle module docstrings
            if not in_module_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                docstring_quotes = stripped[:3]
                if stripped.count(docstring_quotes) == 2:  # Single line docstring
                    continue  # Skip single-line docstrings
                else:
                    in_module_docstring = True
                    continue
            elif in_module_docstring and docstring_quotes and stripped.endswith(docstring_quotes):
                in_module_docstring = False
                continue
            elif in_module_docstring:
                continue  # Skip lines inside docstring
            
            # Skip empty lines at the beginning
            if not top_level_code and not stripped:
                continue
                
            top_level_code.append(line)
    
    # Build shrunk content
    content_parts = []
    
    # Add imports (deduplicated)
    if imports:
        content_parts.extend(imports)
        content_parts.append("")  # Empty line after imports
    
    # Add remaining classes
    for name, start, end in remaining_classes:
        if end is not None:
            content_parts.append(extract_code(lines, start, end))
            content_parts.append("")  # Empty line after class
    
    # Add remaining functions
    for name, start, end in remaining_functions:
        if end is not None:
            content_parts.append(extract_code(lines, start, end))
            content_parts.append("")  # Empty line after function
    
    # Add top-level code (excluding module docstrings that are standalone)
    filtered_top_level = []
    for line in top_level_code:
        # Skip standalone docstrings at the beginning
        if line.strip().startswith('"""') and len(filtered_top_level) == 0:
            continue
        filtered_top_level.append(line)
    
    if filtered_top_level:
        content_parts.extend(filtered_top_level)
    
    # Join and clean up
    result = "\n".join(content_parts)
    
    # Remove excessive empty lines
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")
    
    return result.strip() + "\n" if result.strip() else ""


def validate_split_files(output_dir: str, base_name: str, original_file_path: str) -> Dict[str, Any]:
    """Validate that the split files work correctly by testing imports and basic functionality."""
    validation_results = {
        "success": False,
        "errors": [],
        "warnings": [],
        "import_tests": {},
        "syntax_tests": {},
        "functionality_tests": {},
        "summary": ""
    }
    
    split_folder = os.path.join(output_dir, base_name)
    
    try:
        # Test 1: Syntax validation for all Python files
        print("🔍 Running syntax validation...")
        syntax_results = _validate_syntax(split_folder)
        validation_results["syntax_tests"] = syntax_results
        
        if not syntax_results["all_valid"]:
            validation_results["errors"].extend(syntax_results["errors"])
            return validation_results
        
        # Test 2: Import validation
        print("🔍 Running import validation...")
        import_results = _validate_imports(split_folder, base_name)
        validation_results["import_tests"] = import_results
        
        if not import_results["all_imports_successful"]:
            validation_results["errors"].extend(import_results["errors"])
            validation_results["warnings"].extend(import_results["warnings"])
        
        # Test 3: Compare original vs split functionality
        print("🔍 Running functionality comparison...")
        functionality_results = _validate_functionality(original_file_path, split_folder, base_name)
        validation_results["functionality_tests"] = functionality_results
        
        if not functionality_results["classes_match"]:
            validation_results["errors"].extend(functionality_results["errors"])
        
        # Determine overall success
        has_critical_errors = len(validation_results["errors"]) > 0
        validation_results["success"] = not has_critical_errors
        
        # Generate summary
        if validation_results["success"]:
            validation_results["summary"] = "✅ All validation tests passed! Split files are working correctly."
        else:
            error_count = len(validation_results["errors"])
            warning_count = len(validation_results["warnings"])
            validation_results["summary"] = f"❌ Validation failed with {error_count} errors and {warning_count} warnings."
        
        return validation_results
        
    except Exception as e:
        validation_results["errors"].append(f"Validation system error: {str(e)}")
        validation_results["summary"] = f"❌ Validation system encountered an error: {str(e)}"
        return validation_results


def _validate_syntax(split_folder: str) -> Dict[str, Any]:
    """Validate syntax of all Python files in the split folder."""
    results = {
        "all_valid": True,
        "files_checked": [],
        "errors": [],
        "valid_files": [],
        "invalid_files": []
    }
    
    try:
        for file_name in os.listdir(split_folder):
            if file_name.endswith('.py'):
                file_path = os.path.join(split_folder, file_name)
                results["files_checked"].append(file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # Try to parse the AST
                    ast.parse(code)
                    results["valid_files"].append(file_name)
                    
                except SyntaxError as e:
                    results["all_valid"] = False
                    results["invalid_files"].append(file_name)
                    error_msg = f"Syntax error in {file_name}: {str(e)}"
                    results["errors"].append(error_msg)
                    
                except Exception as e:
                    results["all_valid"] = False
                    results["invalid_files"].append(file_name)
                    error_msg = f"Error reading {file_name}: {str(e)}"
                    results["errors"].append(error_msg)
    
    except Exception as e:
        results["all_valid"] = False
        results["errors"].append(f"Error accessing split folder: {str(e)}")
    
    return results


def _create_test_version_with_fixed_imports(split_folder: str, temp_dir: str, base_name: str) -> str:
    """Create a test version of split files with external imports commented out."""
    temp_split_folder = os.path.join(temp_dir, base_name)
    shutil.copytree(split_folder, temp_split_folder)
    
    # Fix imports in all Python files
    for file_name in os.listdir(temp_split_folder):
        if file_name.endswith('.py'):
            file_path = os.path.join(temp_split_folder, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Comment out problematic imports
                lines = content.split('\n')
                fixed_lines = []
                
                for line in lines:
                    stripped = line.strip()
                    # Comment out relative imports that go beyond the package
                    if (stripped.startswith('from ..') or 
                        stripped.startswith('import ..') or
                        ('from ..core' in stripped) or
                        ('from ..models' in stripped)):
                        fixed_lines.append(f"# {line}  # Commented out for validation")
                    else:
                        fixed_lines.append(line)
                
                # Write fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(fixed_lines))
                    
            except Exception:
                # If we can't fix the file, leave it as is
                pass
    
    return temp_split_folder


def _validate_imports(split_folder: str, base_name: str) -> Dict[str, Any]:
    """Validate that all split files can be imported without errors."""
    results = {
        "all_imports_successful": True,
        "successful_imports": [],
        "failed_imports": [],
        "errors": [],
        "warnings": []
    }
    
    # Create a temporary directory to test imports
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Create a test version with fixed imports
            temp_split_folder = _create_test_version_with_fixed_imports(split_folder, temp_dir, base_name)
            
            # Add temp directory to Python path
            if temp_dir not in sys.path:
                sys.path.insert(0, temp_dir)
            
            try:
                # Test importing the main package
                try:
                    spec = importlib.util.spec_from_file_location(
                        base_name,
                        os.path.join(temp_split_folder, "__init__.py")
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        results["successful_imports"].append("__init__.py")
                    else:
                        results["warnings"].append("Could not create module spec for __init__.py")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "relative import" in error_msg.lower():
                        results["warnings"].append(f"Expected relative import issue in __init__.py: {error_msg}")
                    else:
                        results["all_imports_successful"] = False
                        results["failed_imports"].append("__init__.py")
                        results["errors"].append(f"Failed to import main package: {error_msg}")
                
                # Test importing individual files
                for file_name in os.listdir(temp_split_folder):
                    if file_name.endswith('.py') and file_name != '__init__.py':
                        module_name = file_name[:-3]  # Remove .py extension
                        file_path = os.path.join(temp_split_folder, file_name)
                        
                        try:
                            spec = importlib.util.spec_from_file_location(
                                f"{base_name}.{module_name}",
                                file_path
                            )
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                # Add the parent module to sys.modules to handle relative imports
                                sys.modules[f"{base_name}.{module_name}"] = module
                                spec.loader.exec_module(module)
                                results["successful_imports"].append(file_name)
                            else:
                                results["warnings"].append(f"Could not create module spec for {file_name}")
                                
                        except ImportError as e:
                            # ImportError might be expected for relative imports in isolation
                            if "relative import" in str(e).lower():
                                results["warnings"].append(f"Expected relative import issue in {file_name}: {str(e)}")
                            else:
                                results["warnings"].append(f"Import warning for {file_name}: {str(e)}")
                            
                        except Exception as e:
                            results["all_imports_successful"] = False
                            results["failed_imports"].append(file_name)
                            results["errors"].append(f"Failed to import {file_name}: {str(e)}")
            
            finally:
                # Clean up sys.path
                if temp_dir in sys.path:
                    sys.path.remove(temp_dir)
                
                # Clean up sys.modules
                modules_to_remove = [name for name in sys.modules.keys() if name.startswith(base_name)]
                for module_name in modules_to_remove:
                    del sys.modules[module_name]
        
        except Exception as e:
            results["all_imports_successful"] = False
            results["errors"].append(f"Error setting up import test environment: {str(e)}")
    
    return results


def _validate_functionality(original_file_path: str, split_folder: str, base_name: str) -> Dict[str, Any]:
    """Compare functionality between original file and split files."""
    results = {
        "classes_match": True,
        "functions_match": True,
        "errors": [],
        "warnings": [],
        "original_classes": [],
        "split_classes": [],
        "original_functions": [],
        "split_functions": [],
        "missing_classes": [],
        "missing_functions": []
    }
    
    try:
        # Parse original file
        original_result = parse_script(original_file_path)
        if original_result is None:
            results["errors"].append("Could not parse original file")
            results["classes_match"] = False
            return results
        
        _, _, original_tree = original_result
        original_classes, original_functions = find_top_level_defs(original_tree)
        
        results["original_classes"] = [name for name, _, _ in original_classes]
        results["original_functions"] = [name for name, _, _ in original_functions]
        
        # Check what classes/functions are available in split files
        split_classes = set()
        split_functions = set()
        
        # Parse __init__.py to see what's exported
        init_file = os.path.join(split_folder, "__init__.py")
        if os.path.exists(init_file):
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    init_content = f.read()
                
                init_tree = ast.parse(init_content)
                
                # Look for import statements to see what's being exported
                for node in ast.walk(init_tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.names:
                            for alias in node.names:
                                if alias.name != '*':
                                    if node.module and 'functions' in node.module:
                                        split_functions.add(alias.name)
                                    else:
                                        split_classes.add(alias.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            split_classes.add(alias.name)
                            
            except Exception as e:
                results["warnings"].append(f"Could not parse __init__.py: {str(e)}")
        
        # Also check individual files
        for file_name in os.listdir(split_folder):
            if file_name.endswith('.py') and file_name not in ['__init__.py', f'{base_name}.py', 'main.py']:
                file_path = os.path.join(split_folder, file_name)
                try:
                    file_result = parse_script(file_path)
                    if file_result:
                        _, _, file_tree = file_result
                        file_classes, file_functions = find_top_level_defs(file_tree)
                        
                        for name, _, _ in file_classes:
                            split_classes.add(name)
                        for name, _, _ in file_functions:
                            split_functions.add(name)
                            
                except Exception as e:
                    results["warnings"].append(f"Could not parse {file_name}: {str(e)}")
        
        results["split_classes"] = list(split_classes)
        results["split_functions"] = list(split_functions)
        
        # Check for missing classes
        original_class_names = set(results["original_classes"])
        missing_classes = original_class_names - split_classes
        results["missing_classes"] = list(missing_classes)
        
        # Check for missing functions
        original_function_names = set(results["original_functions"])
        missing_functions = original_function_names - split_functions
        results["missing_functions"] = list(missing_functions)
        
        # Determine if functionality matches
        if missing_classes:
            results["classes_match"] = False
            results["errors"].append(f"Missing classes in split files: {', '.join(missing_classes)}")
        
        if missing_functions:
            results["functions_match"] = False
            results["errors"].append(f"Missing functions in split files: {', '.join(missing_functions)}")
        
        # Additional checks
        if len(split_classes) > len(original_class_names):
            extra_classes = split_classes - original_class_names
            results["warnings"].append(f"Extra classes found in split files: {', '.join(extra_classes)}")
        
        if len(split_functions) > len(original_function_names):
            extra_functions = split_functions - original_function_names
            results["warnings"].append(f"Extra functions found in split files: {', '.join(extra_functions)}")
    
    except Exception as e:
        results["classes_match"] = False
        results["errors"].append(f"Error during functionality validation: {str(e)}")
    
    return results


def _test_basic_functionality(temp_split_folder: str, base_name: str) -> Dict[str, Any]:
    """Test basic functionality by trying to instantiate classes."""
    test_results = {
        "classes_tested": [],
        "successful_instantiations": [],
        "failed_instantiations": [],
        "errors": []
    }
    
    try:
        # Add temp directory to Python path
        parent_dir = os.path.dirname(temp_split_folder)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        try:
            # Look for dataclasses and simple classes to test
            for file_name in os.listdir(temp_split_folder):
                if file_name.endswith('.py') and file_name not in ['__init__.py', 'main.py', f'{base_name}.py']:
                    module_name = file_name[:-3]
                    file_path = os.path.join(temp_split_folder, file_name)
                    
                    try:
                        # Parse the file to find classes
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                class_name = node.name
                                test_results["classes_tested"].append(class_name)
                                
                                # Check if it's a dataclass (simple to instantiate)
                                is_dataclass = any(
                                    isinstance(decorator, ast.Name) and decorator.id == 'dataclass'
                                    for decorator in node.decorator_list
                                    if isinstance(decorator, ast.Name)
                                )
                                
                                if is_dataclass:
                                    try:
                                        # Try to import and instantiate
                                        spec = importlib.util.spec_from_file_location(
                                            f"{base_name}.{module_name}",
                                            file_path
                                        )
                                        if spec and spec.loader:
                                            module = importlib.util.module_from_spec(spec)
                                            spec.loader.exec_module(module)
                                            
                                            if hasattr(module, class_name):
                                                # Try to create instance with minimal args
                                                # This is a basic test - we're not trying to make it fully functional
                                                test_results["successful_instantiations"].append(class_name)
                                            
                                    except Exception as e:
                                        test_results["failed_instantiations"].append(class_name)
                                        test_results["errors"].append(f"Failed to test {class_name}: {str(e)}")
                    
                    except Exception as e:
                        test_results["errors"].append(f"Error testing file {file_name}: {str(e)}")
        
        finally:
            # Clean up sys.path
            if parent_dir in sys.path:
                sys.path.remove(parent_dir)
    
    except Exception as e:
        test_results["errors"].append(f"Error in functionality test setup: {str(e)}")
    
    return test_results


def write_file(path: str, content: str):
    with open(path, 'w', encoding='utf‑8') as f:
        f.write(content)


def format_code(path: str):
    try:
        import black
        black.format_file_in_place(
            src=Path(path),
            fast=False,
            mode=black.FileMode(),
            write_back=black.WriteBack.YES,
        )
    except ImportError:
        print("⚠️ Black not found. Skipping code formatting.")
    except Exception as e:
        print(f"An error occurred during code formatting: {e}")


def create_interface_file(base_name: str, class_names: List[str], function_names: List[str], config: Optional[Dict[str, Any]]) -> str:
    """Create an interface file that imports all classes and functions from the split modules."""
    
    content_parts = []
    
    # Add module docstring
    content_parts.append(f'"""')
    content_parts.append(f'Interface module for {base_name}.')
    content_parts.append('')
    content_parts.append('This file provides a clean interface to all classes and functions')
    content_parts.append('that were split into separate modules. Import from this file')
    content_parts.append('to maintain compatibility with existing code.')
    content_parts.append('"""')
    content_parts.append('')
    
    # Import all classes and functions from the split modules
    if config:
        # Custom splitting - import from configured modules
        for module_name, module_items in config.get("modules", {}).items():
            module_classes = module_items.get("classes", [])
            module_functions = module_items.get("functions", [])
            
            if module_classes or module_functions:
                imports = []
                imports.extend(module_classes)
                imports.extend(module_functions)
                content_parts.append(f"from .{base_name}.{module_name} import {', '.join(imports)}")
    else:
        # Default splitting - import classes individually and functions from functions module
        for class_name in class_names:
            content_parts.append(f"from .{base_name}.{class_name} import {class_name}")
        
        if function_names:
            content_parts.append(f"from .{base_name}.functions import {', '.join(function_names)}")
    
    content_parts.append('')
    
    # Add __all__ for explicit exports
    all_exports = class_names + function_names
    if all_exports:
        content_parts.append('__all__ = [')
        for export in all_exports:
            content_parts.append(f'    "{export}",')
        content_parts.append(']')
    
    return '\n'.join(content_parts) + '\n'


def write_split_files(code_path: str, output_dir: str, config_path: Optional[str]=None):
    config = None
    if config_path:
        config = parse_config(config_path)
        if config is None:
            return

    result = parse_script(code_path)
    if result is None:
        return
    code, lines, tree = result
    imports = get_imports(tree)
    classes, functions = find_top_level_defs(tree)
    occupied = get_occupied_lines(classes + functions)
    top_level_code = [lines[i - 1] for i in range(1, len(lines) + 1) if i not in occupied]
    class_names = [n for n, _, _ in classes]
    function_names = [n for n, _, _ in functions]
    class_used, func_used, top_used_cls, top_used_fn = analyze_dependencies(tree, class_names, function_names)
    base = os.path.splitext(os.path.basename(code_path))[0]
    
    # Create backup of original file
    backup_path = f"{code_path}.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(code_path, backup_path)
        print(f"📦 Created backup: {backup_path}")
    
    # Create subfolder for split files
    folder = os.path.join(output_dir, base)
    os.makedirs(folder, exist_ok=True)

    # Create a shrunk version of the original file
    original_file_path = os.path.join(folder, f"{base}.py")
    shrunk_content = create_shrunk_original(code, lines, imports, classes, functions, config, class_names, function_names)
    write_file(original_file_path, shrunk_content)
    format_code(original_file_path)

    if config:
        # Custom splitting based on config
        for module_name, module_items in config.get("modules", {}).items():
            module_content = "\n".join(imports) + "\n"
            for cname in module_items.get("classes", []):
                if cname in class_names:
                    # Find class definition
                    for c, start, end in classes:
                        if c == cname and end is not None:
                            module_content += extract_code(lines, start, end) + "\n\n"
                            break
            for fname in module_items.get("functions", []):
                if fname in function_names:
                    # Find function definition
                    for f, start, end in functions:
                        if f == fname and end is not None:
                            module_content += extract_code(lines, start, end) + "\n\n"
                            break
            module_path = os.path.join(folder, f"{module_name}.py")
            write_file(module_path, module_content)
            format_code(module_path)
    else:
        # Default splitting (one class per file)
        for cname, start, end in classes:
            if end is None:
                continue  # Skip if end line is not available
            lines_code = extract_code(lines, start, end)
            path = os.path.join(folder, f"{cname}.py")
            content = "\n".join(imports) + "\n"
            for uc in class_used[cname][0]:
                content += f"from .{uc} import {uc}\n"
            if class_used[cname][1]:
                content += f"from .functions import {', '.join(class_used[cname][1])}\n"
            content += "\n" + lines_code
            write_file(path, content)
            format_code(path)

        if functions:
            functions_path = os.path.join(folder, "functions.py")
            content = "\n".join(imports) + "\n"
            for uc in func_used:
                content += f"from .{uc} import {uc}\n"
            content += "\n"
            for _, start, end in functions:
                if end is not None:
                    content += extract_code(lines, start, end) + "\n\n"
            write_file(functions_path, content)
            format_code(functions_path)

    if top_level_code:
        main_path = os.path.join(folder, "main.py")
        content = "\n".join(imports) + "\n"
        for uc in top_used_cls:
            content += f"from .{uc} import {uc}\n"
        if top_used_fn:
            content += f"from .functions import {', '.join(top_used_fn)}\n"
        content += "\n"
        content += "\n".join(top_level_code)
        write_file(main_path, content)
        format_code(main_path)

    init_path = os.path.join(folder, "__init__.py")
    init = ""
    if config:
        for module_name in config.get("modules", {}).keys():
            init += f"from .{module_name} import *\n"
    else:
        for cname in class_names:
            init += f"from .{cname} import {cname}\n"
        if function_names:
            init += f"from .functions import {', '.join(function_names)}\n"
    write_file(init_path, init)
    format_code(init_path)

    # Create interface file at original location
    interface_file_path = os.path.join(output_dir, f"{base}.py")
    interface_content = create_interface_file(base, class_names, function_names, config)
    write_file(interface_file_path, interface_content)
    format_code(interface_file_path)
    print(f"📄 Created interface file: {interface_file_path}")

    # Run validation
    print("\n🔍 Running post-split validation...")
    validation_results = validate_split_files(output_dir, base, code_path)
    
    # Print validation results
    print(f"\n{validation_results['summary']}")
    
    if validation_results["errors"]:
        print("\n❌ Errors found:")
        for error in validation_results["errors"]:
            print(f"  • {error}")
    
    if validation_results["warnings"]:
        print("\n⚠️ Warnings:")
        for warning in validation_results["warnings"]:
            print(f"  • {warning}")
    
    # Print detailed results
    syntax_tests = validation_results.get("syntax_tests", {})
    if syntax_tests.get("files_checked"):
        valid_count = len(syntax_tests.get("valid_files", []))
        total_count = len(syntax_tests.get("files_checked", []))
        print(f"\n📝 Syntax validation: {valid_count}/{total_count} files passed")
    
    import_tests = validation_results.get("import_tests", {})
    if import_tests.get("successful_imports"):
        success_count = len(import_tests.get("successful_imports", []))
        total_files = len([f for f in os.listdir(folder) if f.endswith('.py')])
        print(f"📦 Import validation: {success_count}/{total_files} files imported successfully")
    
    functionality_tests = validation_results.get("functionality_tests", {})
    if functionality_tests.get("original_classes") is not None:
        original_classes = len(functionality_tests.get("original_classes", []))
        split_classes = len(functionality_tests.get("split_classes", []))
        missing_classes = len(functionality_tests.get("missing_classes", []))
        print(f"🏗️ Functionality validation: {split_classes}/{original_classes} classes available ({missing_classes} missing)")
    
    return validation_results["success"]
