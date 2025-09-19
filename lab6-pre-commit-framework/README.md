# Lab 6: Pre-commit Framework

## Learning Objectives

By the end of this lab, you will:
- Understand the pre-commit framework and its benefits
- Install and configure pre-commit with multiple hooks
- Use popular pre-commit hooks for code quality
- Create custom pre-commit hooks
- Manage pre-commit configuration across teams
- Integrate pre-commit with CI/CD pipelines

## Introduction

The pre-commit framework is a powerful tool that manages Git hooks for you. Instead of writing individual hook scripts, you can use a configuration file to specify which hooks to run, and pre-commit handles the installation, updates, and execution.

### Benefits of Pre-commit Framework

1. **Standardized Configuration**: YAML configuration that's easy to share
2. **Automatic Updates**: Hooks can be automatically updated
3. **Language Agnostic**: Supports hooks written in any language
4. **Rich Ecosystem**: Large collection of pre-built hooks
5. **Performance**: Hooks run in isolated environments
6. **CI Integration**: Easy to run the same hooks in CI

## Prerequisites

- Completed Labs 0-5
- Python 3.7+ installed
- Git repository for testing

## Tasks

### Task 1: Install and Configure Pre-commit

1. **Install pre-commit framework**:
   ```bash
   pip install pre-commit
   ```

2. **Create a basic `.pre-commit-config.yaml`**:
   ```yaml
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.4.0
       hooks:
         - id: trailing-whitespace
         - id: end-of-file-fixer
         - id: check-yaml
         - id: check-added-large-files
   ```

3. **Install the hooks**:
   ```bash
   pre-commit install
   ```

4. **Test the configuration**:
   ```bash
   pre-commit run --all-files
   ```

### Task 2: Add Language-Specific Hooks

Extend your `.pre-commit-config.yaml` to include language-specific linters:

1. **Add Python hooks**:
   ```yaml
   repos:
     # ... existing repos ...
     - repo: https://github.com/psf/black
       rev: 22.10.0
       hooks:
         - id: black
           language_version: python3
     
     - repo: https://github.com/pycqa/flake8
       rev: 5.0.4
       hooks:
         - id: flake8
           additional_dependencies: [flake8-docstrings]
     
     - repo: https://github.com/pycqa/isort
       rev: 5.10.1
       hooks:
         - id: isort
           args: ["--profile", "black"]
   ```

2. **Add JavaScript/TypeScript hooks** (if applicable):
   ```yaml
   - repo: https://github.com/pre-commit/mirrors-eslint
     rev: v8.28.0
     hooks:
       - id: eslint
         files: \.(js|ts|jsx|tsx)$
         types: [file]
   ```

3. **Test the new configuration**:
   ```bash
   pre-commit run --all-files
   ```

### Task 3: Create a Custom Pre-commit Hook

1. **Create a custom hook script** (`hooks/check-commit-message.py`):
   ```python
   #!/usr/bin/env python3
   """Custom hook to validate commit messages."""
   
   import sys
   import re
   
   def check_commit_message(filename):
       with open(filename, 'r') as f:
           message = f.read().strip()
       
       # Check for Jira ticket format
       pattern = r'^[A-Z]+-\d+:'
       if not re.match(pattern, message):
           print("Commit message must start with Jira ticket (e.g., 'PROJ-123: ...')")
           return 1
       
       return 0
   
   if __name__ == '__main__':
       sys.exit(check_commit_message(sys.argv[1]))
   ```

2. **Add the custom hook to your configuration**:
   ```yaml
   - repo: local
     hooks:
       - id: check-commit-message
         name: Check commit message format
         entry: python hooks/check-commit-message.py
         language: system
         stages: [commit-msg]
   ```

### Task 4: Advanced Configuration

1. **Add hook arguments and file filtering**:
   ```yaml
   - repo: https://github.com/psf/black
     rev: 22.10.0
     hooks:
       - id: black
         args: [--line-length=88, --target-version=py38]
         files: \.py$
   ```

2. **Configure specific hooks for specific file types**:
   ```yaml
   - repo: https://github.com/pre-commit/pre-commit-hooks
     rev: v4.4.0
     hooks:
       - id: check-json
         files: \.json$
       - id: check-toml
         files: \.toml$
       - id: check-xml
         files: \.xml$
   ```

3. **Add security scanning**:
   ```yaml
   - repo: https://github.com/PyCQA/bandit
     rev: 1.7.4
     hooks:
       - id: bandit
         args: ['-r', '.']
         exclude: tests/
   ```

### Task 5: Team Configuration Management

1. **Create a shared configuration template**:
   ```yaml
   # .pre-commit-config-template.yaml
   default_stages: [commit, push]
   default_language_version:
     python: python3.8
   
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v4.4.0
       hooks:
         - id: trailing-whitespace
         - id: end-of-file-fixer
         - id: check-merge-conflict
         - id: check-case-conflict
         - id: check-yaml
           args: ['--unsafe']
         - id: check-toml
         - id: check-json
         - id: pretty-format-json
           args: ['--autofix']
         - id: check-added-large-files
           args: ['--maxkb=500']
         - id: check-docstring-first
         - id: debug-statements
   
     - repo: https://github.com/psf/black
       rev: 22.10.0
       hooks:
         - id: black
           language_version: python3
   
     - repo: https://github.com/pycqa/isort
       rev: 5.10.1
       hooks:
         - id: isort
           args: ["--profile", "black", "--check-only", "--diff"]
   
     - repo: https://github.com/pycqa/flake8
       rev: 5.0.4
       hooks:
         - id: flake8
           additional_dependencies:
             - flake8-docstrings
             - flake8-import-order
             - flake8-bugbear
   
     - repo: https://github.com/pre-commit/mirrors-mypy
       rev: v0.991
       hooks:
         - id: mypy
           additional_dependencies: [types-requests]
   ```

2. **Create setup script for new team members**:
   ```bash
   #!/bin/bash
   # setup-pre-commit.sh
   
   echo "Setting up pre-commit for this repository..."
   
   # Install pre-commit if not already installed
   if ! command -v pre-commit &> /dev/null; then
       echo "Installing pre-commit..."
       pip install pre-commit
   fi
   
   # Copy template if no config exists
   if [ ! -f .pre-commit-config.yaml ]; then
       cp .pre-commit-config-template.yaml .pre-commit-config.yaml
       echo "Created .pre-commit-config.yaml from template"
   fi
   
   # Install hooks
   pre-commit install
   pre-commit install --hook-type commit-msg
   
   # Run against all files to ensure everything works
   echo "Running pre-commit on all files..."
   pre-commit run --all-files
   
   echo "Pre-commit setup complete!"
   ```

### Task 6: CI/CD Integration

1. **Add pre-commit to GitHub Actions** (`.github/workflows/pre-commit.yml`):
   ```yaml
   name: Pre-commit
   
   on:
     pull_request:
     push:
       branches: [main]
   
   jobs:
     pre-commit:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: 3.x
         - uses: pre-commit/action@v3.0.0
   ```

2. **Add pre-commit to GitLab CI** (`.gitlab-ci.yml`):
   ```yaml
   pre-commit:
     image: python:3.8
     before_script:
       - pip install pre-commit
     script:
       - pre-commit run --all-files
     only:
       - merge_requests
       - main
   ```

## Stretch Goals

### 1. Custom Hook Repository

Create your own repository of custom hooks:

1. **Create hook repository structure**:
   ```
   my-custom-hooks/
   ├── .pre-commit-hooks.yaml
   ├── hooks/
   │   ├── check-api-keys.py
   │   ├── validate-json-schema.py
   │   └── check-license-headers.py
   └── README.md
   ```

2. **Define hooks in `.pre-commit-hooks.yaml`**:
   ```yaml
   - id: check-api-keys
     name: Check for exposed API keys
     entry: hooks/check-api-keys.py
     language: python
     files: \.(py|js|ts|yaml|yml|json)$
   
   - id: validate-json-schema
     name: Validate JSON against schema
     entry: hooks/validate-json-schema.py
     language: python
     files: \.json$
     require_serial: true
   ```

### 2. Performance Optimization

1. **Configure hook caching**:
   ```yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 22.10.0
       hooks:
         - id: black
           # Only run on Python files that have changed
           files: \.py$
           # Skip if no Python files changed
           exclude_types: [markdown, yaml]
   ```

2. **Parallel execution configuration**:
   ```bash
   # Run hooks in parallel when possible
   pre-commit run --all-files --jobs 4
   ```

### 3. Hook Development Best Practices

Create comprehensive custom hooks following best practices:

1. **Error handling and user feedback**
2. **Configuration file support**
3. **Multiple file format support**
4. **Integration with external tools**
5. **Performance optimization**

## Testing Your Implementation

1. **Test basic functionality**:
   ```bash
   # Make a change that should trigger hooks
   echo "print('hello world')" > test.py
   git add test.py
   git commit -m "Add test file"
   ```

2. **Test hook updates**:
   ```bash
   pre-commit autoupdate
   pre-commit run --all-files
   ```

3. **Test specific hooks**:
   ```bash
   pre-commit run black --all-files
   pre-commit run flake8 --all-files
   ```

4. **Test bypassing hooks** (for emergencies):
   ```bash
   git commit -m "Emergency fix" --no-verify
   ```

## Common Issues and Troubleshooting

### Issue 1: Hook Installation Fails
```bash
# Clear pre-commit cache and reinstall
pre-commit clean
pre-commit install --install-hooks
```

### Issue 2: Hooks Run Slowly
```bash
# Check which hooks are taking time
pre-commit run --all-files --verbose
```

### Issue 3: Configuration Conflicts
```bash
# Validate configuration
pre-commit validate-config
```

### Issue 4: Python Version Issues
```bash
# Specify Python version explicitly
pre-commit run --all-files --hook-stage manual
```

## Best Practices

1. **Start Small**: Begin with basic hooks and gradually add more
2. **Team Agreement**: Ensure all team members agree on the hook configuration
3. **Regular Updates**: Update hook versions regularly with `pre-commit autoupdate`
4. **Fast Hooks**: Keep hooks fast to avoid slowing down development
5. **Clear Error Messages**: Ensure hooks provide helpful error messages
6. **Bypass Mechanism**: Document when and how to bypass hooks in emergencies
7. **CI Integration**: Run the same hooks in CI to catch any bypassed commits

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Supported Hooks](https://pre-commit.com/hooks.html)
- [Writing Custom Hooks](https://pre-commit.com/#new-hooks)
- [Pre-commit Hook Repository Template](https://github.com/pre-commit/pre-commit-hook-template)

## Next Steps

After completing this lab:
1. Proceed to **Lab 7: GitLeaks Integration** to add secret scanning
2. Consider setting up pre-commit for your real projects
3. Explore creating custom hooks for your team's specific needs