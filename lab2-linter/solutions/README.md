# Lab 2 Solutions

## Complete Solution Scripts

### Task 1: Basic Python Syntax Checker
```python
#!/usr/bin/env python3
import subprocess
import sys
import ast

def get_staged_python_files():
    """Get list of staged Python files"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.py') and f]
    except subprocess.CalledProcessError:
        return []

def check_python_syntax(filename):
    """Check if a Python file has valid syntax"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    print("🐍 Python Syntax Checker")
    print("=" * 30)
    
    python_files = get_staged_python_files()
    
    if not python_files:
        print("ℹ️  No Python files to check")
        return 0
    
    print(f"📝 Checking {len(python_files)} Python file(s)...")
    
    errors = []
    for filename in python_files:
        print(f"   Checking {filename}...", end=" ")
        is_valid, error = check_python_syntax(filename)
        
        if is_valid:
            print("✅")
        else:
            print("❌")
            errors.append(f"{filename}: {error}")
    
    if errors:
        print("\n🚨 Syntax errors found:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 Fix syntax errors before committing")
        return 1
    
    print("✅ All Python files have valid syntax!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Task 2: Advanced Style Checker
```python
#!/usr/bin/env python3
import subprocess
import sys
import ast
import re

class StyleChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def check_line_length(self, lines, max_length=79):
        """Check for lines that are too long"""
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > max_length:
                self.errors.append(f"Line {i}: Line too long ({len(line.rstrip())} > {max_length})")
    
    def check_indentation(self, lines):
        """Check for inconsistent indentation"""
        for i, line in enumerate(lines, 1):
            if line.startswith(' ') and line.startswith('\t'):
                self.errors.append(f"Line {i}: Mixed tabs and spaces")
            elif line.startswith('\t'):
                self.warnings.append(f"Line {i}: Using tabs instead of spaces")
    
    def check_trailing_whitespace(self, lines):
        """Check for trailing whitespace"""
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip('\n'):
                self.errors.append(f"Line {i}: Trailing whitespace")
    
    def check_imports(self, lines):
        """Check import organization"""
        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append((i, stripped))
        
        # Check for imports after non-import statements
        found_non_import = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                if not (stripped.startswith('import ') or stripped.startswith('from ')):
                    found_non_import = True
                elif found_non_import:
                    self.warnings.append(f"Line {i}: Import not at top of file")
    
    def check_naming_conventions(self, content):
        """Check basic naming conventions"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        self.warnings.append(f"Function '{node.name}': Should use snake_case")
                elif isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        self.warnings.append(f"Class '{node.name}': Should use PascalCase")
        except SyntaxError:
            pass  # Syntax errors will be caught elsewhere

def get_staged_python_files():
    """Get list of staged Python files"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.py') and f]
    except subprocess.CalledProcessError:
        return []

def check_python_syntax(filename):
    """Check if a Python file has valid syntax"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def check_code_style(filename):
    """Check code style for a Python file"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
            lines = content.splitlines()
        
        checker = StyleChecker()
        checker.check_line_length(lines)
        checker.check_indentation(lines)
        checker.check_trailing_whitespace(lines)
        checker.check_imports(lines)
        checker.check_naming_conventions(content)
        
        return checker.errors, checker.warnings
    except Exception as e:
        return [f"Error checking style: {e}"], []

def main():
    print("🐍 Python Linter")
    print("=" * 20)
    
    python_files = get_staged_python_files()
    
    if not python_files:
        print("ℹ️  No Python files to check")
        return 0
    
    print(f"📝 Checking {len(python_files)} Python file(s)...")
    
    total_errors = []
    total_warnings = []
    
    for filename in python_files:
        print(f"\n📄 {filename}")
        
        # Check syntax first
        is_valid, syntax_error = check_python_syntax(filename)
        if not is_valid:
            total_errors.append(f"{filename}: {syntax_error}")
            print(f"   ❌ Syntax Error: {syntax_error}")
            continue
        
        # Check style
        errors, warnings = check_code_style(filename)
        
        if errors:
            total_errors.extend([f"{filename}: {error}" for error in errors])
            for error in errors:
                print(f"   ❌ {error}")
        
        if warnings:
            total_warnings.extend([f"{filename}: {warning}" for warning in warnings])
            for warning in warnings:
                print(f"   ⚠️  {warning}")
        
        if not errors and not warnings:
            print("   ✅ All checks passed")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Errors: {len(total_errors)}")
    print(f"   Warnings: {len(total_warnings)}")
    
    if total_errors:
        print("\n🚨 Fix these errors before committing:")
        for error in total_errors[:5]:  # Show first 5 errors
            print(f"   {error}")
        if len(total_errors) > 5:
            print(f"   ... and {len(total_errors) - 5} more")
        return 1
    
    if total_warnings:
        print("\n💡 Consider fixing these warnings:")
        for warning in total_warnings[:3]:  # Show first 3 warnings
            print(f"   {warning}")
        if len(total_warnings) > 3:
            print(f"   ... and {len(total_warnings) - 3} more")
    
    print("✅ Code quality checks passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Task 3: Complete Configurable Linter
```python
#!/usr/bin/env python3
import subprocess
import sys
import ast
import re
import configparser
import os
import json
from pathlib import Path

class LinterConfig:
    def __init__(self, config_file='.pylint-config'):
        self.config = configparser.ConfigParser()
        
        # Set defaults
        self.max_line_length = 79
        self.allow_tabs = False
        self.check_naming = True
        self.check_syntax = True
        self.check_imports = True
        self.check_trailing_whitespace = True
        self.check_docstrings = False
        self.check_complexity = False
        self.warnings_as_errors = False
        self.max_errors_shown = 5
        self.exclude_patterns = []
        
        # Load config file if it exists
        if os.path.exists(config_file):
            self.config.read(config_file)
            self._load_config()
    
    def _load_config(self):
        if 'style' in self.config:
            style = self.config['style']
            self.max_line_length = style.getint('max_line_length', self.max_line_length)
            self.allow_tabs = style.getboolean('allow_tabs', self.allow_tabs)
            self.check_naming = style.getboolean('check_naming', self.check_naming)
        
        if 'checks' in self.config:
            checks = self.config['checks']
            self.check_syntax = checks.getboolean('check_syntax', self.check_syntax)
            self.check_imports = checks.getboolean('check_imports', self.check_imports)
            self.check_trailing_whitespace = checks.getboolean('check_trailing_whitespace', self.check_trailing_whitespace)
            self.check_docstrings = checks.getboolean('check_docstrings', self.check_docstrings)
            self.check_complexity = checks.getboolean('check_complexity', self.check_complexity)
        
        if 'behavior' in self.config:
            behavior = self.config['behavior']
            self.warnings_as_errors = behavior.getboolean('warnings_as_errors', self.warnings_as_errors)
            self.max_errors_shown = behavior.getint('max_errors_shown', self.max_errors_shown)
            exclude_str = behavior.get('exclude_patterns', '')
            if exclude_str:
                self.exclude_patterns = [p.strip() for p in exclude_str.split(',')]

class ComplexityChecker:
    """Check cyclomatic complexity of functions"""
    
    def __init__(self, max_complexity=10):
        self.max_complexity = max_complexity
    
    def check_complexity(self, tree):
        """Check complexity of all functions in the AST"""
        warnings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > self.max_complexity:
                    warnings.append(f"Function '{node.name}': Complexity {complexity} > {self.max_complexity}")
        return warnings
    
    def _calculate_complexity(self, node):
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class StyleChecker:
    def __init__(self, config):
        self.config = config
        self.errors = []
        self.warnings = []
    
    def check_line_length(self, lines):
        """Check for lines that are too long"""
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > self.config.max_line_length:
                self.errors.append(f"Line {i}: Line too long ({len(line.rstrip())} > {self.config.max_line_length})")
    
    def check_indentation(self, lines):
        """Check for inconsistent indentation"""
        for i, line in enumerate(lines, 1):
            if line.startswith(' ') and '\t' in line[:len(line) - len(line.lstrip())]:
                self.errors.append(f"Line {i}: Mixed tabs and spaces")
            elif line.startswith('\t') and not self.config.allow_tabs:
                self.warnings.append(f"Line {i}: Using tabs instead of spaces")
    
    def check_trailing_whitespace(self, lines):
        """Check for trailing whitespace"""
        if not self.config.check_trailing_whitespace:
            return
            
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip('\n'):
                self.errors.append(f"Line {i}: Trailing whitespace")
    
    def check_imports(self, lines):
        """Check import organization"""
        if not self.config.check_imports:
            return
            
        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                import_lines.append((i, stripped))
        
        # Check for imports after non-import statements
        found_non_import = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                if not (stripped.startswith('import ') or stripped.startswith('from ')):
                    found_non_import = True
                elif found_non_import:
                    self.warnings.append(f"Line {i}: Import not at top of file")
    
    def check_naming_conventions(self, content):
        """Check basic naming conventions"""
        if not self.config.check_naming:
            return
            
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        self.warnings.append(f"Function '{node.name}': Should use snake_case")
                elif isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        self.warnings.append(f"Class '{node.name}': Should use PascalCase")
        except SyntaxError:
            pass  # Syntax errors will be caught elsewhere
    
    def check_docstrings(self, content):
        """Check for missing docstrings"""
        if not self.config.check_docstrings:
            return
            
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        self.warnings.append(f"{node.__class__.__name__} '{node.name}': Missing docstring")
        except SyntaxError:
            pass
    
    def check_complexity(self, content):
        """Check cyclomatic complexity"""
        if not self.config.check_complexity:
            return
            
        try:
            tree = ast.parse(content)
            complexity_checker = ComplexityChecker()
            complexity_warnings = complexity_checker.check_complexity(tree)
            self.warnings.extend(complexity_warnings)
        except SyntaxError:
            pass

def get_staged_python_files():
    """Get list of staged Python files"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.py') and f]
    except subprocess.CalledProcessError:
        return []

def should_exclude_file(filename, exclude_patterns):
    """Check if file should be excluded based on patterns"""
    for pattern in exclude_patterns:
        if re.search(pattern, filename):
            return True
    return False

def check_python_syntax(filename):
    """Check if a Python file has valid syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def check_code_style(filename, config):
    """Check code style for a Python file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        checker = StyleChecker(config)
        checker.check_line_length(lines)
        checker.check_indentation(lines)
        checker.check_trailing_whitespace(lines)
        checker.check_imports(lines)
        checker.check_naming_conventions(content)
        checker.check_docstrings(content)
        checker.check_complexity(content)
        
        return checker.errors, checker.warnings
    except Exception as e:
        return [f"Error checking style: {e}"], []

def generate_report(total_errors, total_warnings, config):
    """Generate a detailed report of all issues"""
    report = {
        'summary': {
            'total_errors': len(total_errors),
            'total_warnings': len(total_warnings),
            'config': {
                'max_line_length': config.max_line_length,
                'warnings_as_errors': config.warnings_as_errors
            }
        },
        'errors': total_errors,
        'warnings': total_warnings
    }
    
    # Save report to file
    with open('.git/lint_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    # Load configuration
    config = LinterConfig()
    
    print("🐍 Advanced Python Linter")
    print("=" * 30)
    print(f"📋 Config: max_line_length={config.max_line_length}, "
          f"warnings_as_errors={config.warnings_as_errors}")
    
    python_files = get_staged_python_files()
    
    if not python_files:
        print("ℹ️  No Python files to check")
        return 0
    
    # Filter out excluded files
    filtered_files = [f for f in python_files if not should_exclude_file(f, config.exclude_patterns)]
    excluded_count = len(python_files) - len(filtered_files)
    
    if excluded_count > 0:
        print(f"📋 Excluded {excluded_count} file(s) based on patterns")
    
    if not filtered_files:
        print("ℹ️  All Python files excluded by patterns")
        return 0
    
    print(f"📝 Checking {len(filtered_files)} Python file(s)...")
    
    total_errors = []
    total_warnings = []
    
    for filename in filtered_files:
        print(f"\n📄 {filename}")
        
        # Check syntax first (if enabled)
        if config.check_syntax:
            is_valid, syntax_error = check_python_syntax(filename)
            if not is_valid:
                total_errors.append(f"{filename}: {syntax_error}")
                print(f"   ❌ Syntax Error: {syntax_error}")
                continue
        
        # Check style
        errors, warnings = check_code_style(filename, config)
        
        if errors:
            total_errors.extend([f"{filename}: {error}" for error in errors])
            for error in errors:
                print(f"   ❌ {error}")
        
        if warnings:
            total_warnings.extend([f"{filename}: {warning}" for warning in warnings])
            for warning in warnings:
                print(f"   ⚠️  {warning}")
        
        if not errors and not warnings:
            print("   ✅ All checks passed")
    
    # Generate report
    report = generate_report(total_errors, total_warnings, config)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Errors: {len(total_errors)}")
    print(f"   Warnings: {len(total_warnings)}")
    print(f"   Report saved: .git/lint_report.json")
    
    # Handle warnings as errors if configured
    if config.warnings_as_errors:
        total_errors.extend(total_warnings)
        total_warnings = []
    
    if total_errors:
        print("\n🚨 Fix these errors before committing:")
        for error in total_errors[:config.max_errors_shown]:
            print(f"   {error}")
        if len(total_errors) > config.max_errors_shown:
            print(f"   ... and {len(total_errors) - config.max_errors_shown} more")
        return 1
    
    if total_warnings:
        print("\n💡 Consider fixing these warnings:")
        for warning in total_warnings[:3]:  # Show first 3 warnings
            print(f"   {warning}")
        if len(total_warnings) > 3:
            print(f"   ... and {len(total_warnings) - 3} more")
    
    print("✅ Code quality checks passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Configuration Files

### Basic Configuration (.pylint-config)
```ini
[style]
max_line_length = 88
allow_tabs = false
check_naming = true

[checks]
check_syntax = true
check_imports = true
check_trailing_whitespace = true
check_docstrings = false
check_complexity = false

[behavior]
warnings_as_errors = false
max_errors_shown = 10
exclude_patterns = test_*.py,*_test.py,migrations/*.py
```

### Advanced Configuration
```ini
[style]
max_line_length = 120
allow_tabs = false
check_naming = true

[checks]
check_syntax = true
check_imports = true
check_trailing_whitespace = true
check_docstrings = true
check_complexity = true

[behavior]
warnings_as_errors = false
max_errors_shown = 15
exclude_patterns = test_*.py,*_test.py,migrations/*.py,venv/*,__pycache__/*

[complexity]
max_function_complexity = 15
max_class_complexity = 20
```

## Testing Framework

### Linter Test Suite
```python
#!/usr/bin/env python3
"""
Test suite for the Python linter
"""
import unittest
import tempfile
import os
import subprocess
import sys
from pathlib import Path

class LinterTest(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize git repo
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        import shutil
        shutil.rmtree(self.test_dir)
    
    def create_and_stage_file(self, filename, content):
        """Create a file and stage it"""
        with open(filename, 'w') as f:
            f.write(content)
        subprocess.run(['git', 'add', filename], check=True)
    
    def install_linter(self, linter_content):
        """Install the linter hook"""
        os.makedirs('.git/hooks', exist_ok=True)
        hook_path = '.git/hooks/pre-commit'
        with open(hook_path, 'w') as f:
            f.write(linter_content)
        os.chmod(hook_path, 0o755)
    
    def test_syntax_error_detection(self):
        """Test that syntax errors are detected"""
        bad_python = '''
def hello_world()  # Missing colon
    print("Hello")
'''
        self.create_and_stage_file('bad.py', bad_python)
        
        # Should fail due to syntax error
        result = subprocess.run(['git', 'commit', '-m', 'test'], 
                               capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
    
    def test_style_violations(self):
        """Test that style violations are detected"""
        bad_style = '''
def badFunctionName():  # Bad naming
    very_long_line_that_exceeds_the_normal_length_limit_and_should_trigger_a_warning_about_line_length = "test"
    trailing_spaces = "test"   
'''
        self.create_and_stage_file('style.py', bad_style)
        
        # Test depends on linter configuration
        pass
    
    def test_clean_code_passes(self):
        """Test that clean code passes all checks"""
        clean_python = '''
def hello_world():
    """Print a greeting."""
    print("Hello, World!")

class TestClass:
    """A test class."""
    pass
'''
        self.create_and_stage_file('clean.py', clean_python)
        
        # Should pass all checks
        result = subprocess.run(['git', 'commit', '-m', 'test'], 
                               capture_output=True, text=True)
        # Result depends on linter implementation

if __name__ == '__main__':
    unittest.main()
```

## Advanced Examples

### Multi-language Linter
```python
#!/usr/bin/env python3
"""
Multi-language linter that can handle Python, JavaScript, and more
"""
import subprocess
import sys
import json
import os

class LanguageLinter:
    def __init__(self):
        self.linters = {
            '.py': self.lint_python,
            '.js': self.lint_javascript,
            '.ts': self.lint_typescript,
            '.json': self.lint_json
        }
    
    def get_staged_files(self):
        """Get all staged files with their extensions"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
                capture_output=True, text=True, check=True
            )
            files = result.stdout.strip().split('\n')
            return [f for f in files if f and os.path.exists(f)]
        except subprocess.CalledProcessError:
            return []
    
    def lint_python(self, filename):
        """Lint Python files"""
        # Use existing Python linter logic
        pass
    
    def lint_javascript(self, filename):
        """Lint JavaScript files using ESLint if available"""
        try:
            result = subprocess.run(['npx', 'eslint', filename], 
                                   capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stdout
            return True, None
        except FileNotFoundError:
            return True, "ESLint not available"
    
    def lint_typescript(self, filename):
        """Lint TypeScript files"""
        try:
            result = subprocess.run(['npx', 'tsc', '--noEmit', filename], 
                                   capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stdout
            return True, None
        except FileNotFoundError:
            return True, "TypeScript compiler not available"
    
    def lint_json(self, filename):
        """Validate JSON files"""
        try:
            with open(filename, 'r') as f:
                json.load(f)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON Error: {e}"
    
    def run(self):
        """Run the multi-language linter"""
        files = self.get_staged_files()
        
        if not files:
            print("ℹ️  No files to lint")
            return 0
        
        print("🔍 Multi-language Linter")
        print("=" * 25)
        
        errors = []
        
        for filename in files:
            ext = os.path.splitext(filename)[1]
            
            if ext in self.linters:
                print(f"📄 {filename}")
                success, error = self.linters[ext](filename)
                
                if success:
                    print(f"   ✅ Passed")
                else:
                    print(f"   ❌ Failed: {error}")
                    errors.append(f"{filename}: {error}")
            else:
                print(f"📄 {filename} (no linter available)")
        
        if errors:
            print(f"\n🚨 Found {len(errors)} error(s):")
            for error in errors:
                print(f"   {error}")
            return 1
        
        print("✅ All files passed linting!")
        return 0

if __name__ == "__main__":
    linter = LanguageLinter()
    sys.exit(linter.run())
```