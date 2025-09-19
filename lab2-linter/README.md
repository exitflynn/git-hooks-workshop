# Lab 2: Linter Implementation

## Learning Objectives
- Build a custom Python linter as a Git hook
- Understand code quality enforcement through hooks
- Learn to parse and analyze staged files
- Implement configurable linting rules
- Handle linting errors and warnings appropriately

## Overview

In this lab, you'll create a sophisticated pre-commit hook that acts as a code linter. You'll learn how to analyze staged files, apply coding standards, and provide meaningful feedback to developers. This is a practical example of how Git hooks can enforce code quality in a development workflow.

## Setup

1. Create a new directory for this lab:
   ```bash
   mkdir lab2-practice
   cd lab2-practice
   git init
   git config user.email "test@example.com"
   git config user.name "Test User"
   ```

2. Create a sample Python file to test our linter:
   ```bash
   mkdir src
   ```

## Tasks

### Task 1: Basic Python Syntax Checker

Create a pre-commit hook that checks Python files for syntax errors.

1. Create the hook file:
   ```bash
   touch .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. Implement the basic syntax checker:
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

3. Test with a file that has syntax errors:
   ```bash
   # Create a file with syntax error
   cat > src/bad_syntax.py << 'EOF'
   def hello_world()
       print("Hello World")  # Missing colon above
   EOF
   
   git add src/bad_syntax.py
   git commit -m "Test syntax checker"
   ```

### Task 2: Code Style Checker

Extend the linter to check for common Python style issues.

1. Update the pre-commit hook to include style checks:
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

2. Test with various style issues:
   ```bash
   # Create files with different style issues
   cat > src/style_issues.py << 'EOF'
   import os
   def badFunctionName():  # Should be snake_case
       very_long_line = "This is a very long line that exceeds the 79 character limit and should trigger a warning"
       trailing_spaces = "This line has trailing spaces"   
   	mixed_indentation = "This line uses a tab"  # Mixed with spaces
   
   import sys  # Import not at top
   
   class badClassName:  # Should be PascalCase
       pass
   EOF
   
   git add src/style_issues.py
   git commit -m "Test style checker"
   ```

### Task 3: Configurable Linter

Make the linter configurable through a configuration file.

1. Create a linter configuration file:
   ```bash
   cat > .pylint-config << 'EOF'
   [style]
   max_line_length = 88
   allow_tabs = false
   check_naming = true
   
   [checks]
   check_syntax = true
   check_imports = true
   check_trailing_whitespace = true
   
   [behavior]
   warnings_as_errors = false
   max_errors_shown = 10
   EOF
   ```

2. Update the hook to use configuration:
   ```python
   #!/usr/bin/env python3
   import subprocess
   import sys
   import ast
   import re
   import configparser
   import os
   
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
           self.warnings_as_errors = False
           self.max_errors_shown = 5
           
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
           
           if 'behavior' in self.config:
               behavior = self.config['behavior']
               self.warnings_as_errors = behavior.getboolean('warnings_as_errors', self.warnings_as_errors)
               self.max_errors_shown = behavior.getint('max_errors_shown', self.max_errors_shown)
   
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
   
   def check_code_style(filename, config):
       """Check code style for a Python file"""
       try:
           with open(filename, 'r') as f:
               content = f.read()
               lines = content.splitlines()
           
           checker = StyleChecker(config)
           checker.check_line_length(lines)
           checker.check_indentation(lines)
           checker.check_trailing_whitespace(lines)
           checker.check_imports(lines)
           checker.check_naming_conventions(content)
           
           return checker.errors, checker.warnings
       except Exception as e:
           return [f"Error checking style: {e}"], []
   
   def main():
       # Load configuration
       config = LinterConfig()
       
       print("🐍 Configurable Python Linter")
       print("=" * 35)
       print(f"📋 Config: max_line_length={config.max_line_length}, "
             f"allow_tabs={config.allow_tabs}")
       
       python_files = get_staged_python_files()
       
       if not python_files:
           print("ℹ️  No Python files to check")
           return 0
       
       print(f"📝 Checking {len(python_files)} Python file(s)...")
       
       total_errors = []
       total_warnings = []
       
       for filename in python_files:
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
       
       # Summary
       print(f"\n📊 Summary:")
       print(f"   Errors: {len(total_errors)}")
       print(f"   Warnings: {len(total_warnings)}")
       
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

3. Test the configurable linter:
   ```bash
   git add .pylint-config
   git add src/
   git commit -m "Test configurable linter"
   ```

## Key Concepts

### Linting in Git Hooks

1. **Pre-commit Analysis**: Check staged files before they're committed
2. **Fast Feedback**: Immediate feedback during development
3. **Consistency**: Enforce team-wide coding standards
4. **Automation**: Reduce manual code review overhead

### Staged File Analysis

```python
# Get only staged files
subprocess.run(['git', 'diff', '--cached', '--name-only'])

# Get staged files with their status
subprocess.run(['git', 'diff', '--cached', '--name-status'])
```

### Error vs Warning Handling

- **Errors**: Block the commit (exit code 1)
- **Warnings**: Allow commit but provide feedback (exit code 0)
- **Configurable**: Let teams decide which issues are blocking

### Configuration Best Practices

1. **Use configuration files** for team settings
2. **Provide sensible defaults** for missing config
3. **Allow per-project customization**
4. **Document all configuration options**

## Troubleshooting

### Linter Too Slow?
- Check only staged files, not entire repository
- Limit the scope of checks
- Use efficient parsing algorithms

### False Positives?
- Make rules configurable
- Allow per-line or per-file suppressions
- Provide bypass mechanisms

### Integration Issues?
- Test with various file encodings
- Handle binary files gracefully
- Provide clear error messages

## Best Practices

1. **Start Simple**: Begin with basic checks, add complexity gradually
2. **Be Configurable**: Different projects have different needs
3. **Provide Clear Messages**: Help developers fix issues quickly
4. **Fast Execution**: Keep linting under 2-3 seconds for good UX
5. **Graceful Degradation**: Handle missing dependencies gracefully

## Next Steps

In Lab 3, you'll build a commit message validator that ensures all commits contain proper Jira ticket references and follow conventional commit formats.

## Summary

You've learned:
- How to build a custom Python linter as a Git hook
- How to analyze staged files for code quality issues
- How to create configurable linting rules
- How to provide clear feedback for errors and warnings
- How to integrate automated code quality checks into Git workflow

Your linter can now catch syntax errors, style violations, and enforce coding standards automatically!