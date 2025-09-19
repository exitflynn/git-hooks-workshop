# Lab 5: Post-Checkout Dependencies

## Learning Objectives
- Implement post-checkout hooks for dependency management
- Automatically install dependencies when switching branches
- Handle different dependency managers (pip, npm, etc.)
- Create environment setup automation
- Learn about the post-checkout hook parameters

## Overview

The post-checkout hook runs after a successful `git checkout` and is perfect for automating environment setup tasks. This lab teaches you to automatically install dependencies, switch Python virtual environments, and ensure your development environment matches the branch requirements.

## Setup

```bash
mkdir lab5-practice
cd lab5-practice
git init
git config user.email "test@example.com"
git config user.name "Test User"
```

## Tasks

### Task 1: Basic Post-Checkout Hook

Create a post-checkout hook that detects dependency file changes.

```python
#!/usr/bin/env python3
"""
Post-checkout hook for dependency management
"""
import sys
import os
import subprocess
import json
from pathlib import Path

def main():
    # Post-checkout hook receives 3 arguments:
    # $1 - previous HEAD ref
    # $2 - new HEAD ref  
    # $3 - flag (1 for branch checkout, 0 for file checkout)
    
    if len(sys.argv) != 4:
        return 0
    
    prev_head = sys.argv[1]
    new_head = sys.argv[2]
    branch_checkout = sys.argv[3] == '1'
    
    if not branch_checkout:
        return 0  # Only handle branch checkouts
    
    print("🔄 Post-checkout hook: Checking dependencies...")
    
    # Check for dependency file changes
    dependency_files = [
        'requirements.txt',
        'package.json', 
        'Pipfile',
        'pyproject.toml',
        'environment.yml'
    ]
    
    changed_files = get_changed_files(prev_head, new_head, dependency_files)
    
    if changed_files:
        print(f"📦 Dependency files changed: {', '.join(changed_files)}")
        install_dependencies(changed_files)
    else:
        print("✅ No dependency changes detected")
    
    return 0

def get_changed_files(prev_head, new_head, files_to_check):
    """Check which dependency files changed between refs"""
    changed = []
    
    for file in files_to_check:
        if os.path.exists(file):
            try:
                # Check if file changed between refs
                result = subprocess.run([
                    'git', 'diff', '--name-only', 
                    f'{prev_head}..{new_head}', file
                ], capture_output=True, text=True, check=True)
                
                if result.stdout.strip():
                    changed.append(file)
            except subprocess.CalledProcessError:
                # File might be new, consider it changed
                changed.append(file)
    
    return changed

def install_dependencies(changed_files):
    """Install dependencies based on changed files"""
    for file in changed_files:
        if file == 'requirements.txt':
            install_pip_requirements()
        elif file == 'package.json':
            install_npm_dependencies()
        elif file == 'Pipfile':
            install_pipenv_dependencies()
        elif file == 'environment.yml':
            install_conda_environment()

def install_pip_requirements():
    """Install Python pip requirements"""
    print("🐍 Installing pip requirements...")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Pip requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pip requirements: {e}")
    except FileNotFoundError:
        print("⚠️  pip not found in PATH")

def install_npm_dependencies():
    """Install Node.js npm dependencies"""
    print("📦 Installing npm dependencies...")
    try:
        subprocess.run(['npm', 'install'], check=True)
        print("✅ npm dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install npm dependencies: {e}")
    except FileNotFoundError:
        print("⚠️  npm not found in PATH")

def install_pipenv_dependencies():
    """Install Pipenv dependencies"""
    print("🐍 Installing Pipenv dependencies...")
    try:
        subprocess.run(['pipenv', 'install'], check=True)
        print("✅ Pipenv dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Pipenv dependencies: {e}")
    except FileNotFoundError:
        print("⚠️  pipenv not found in PATH")

def install_conda_environment():
    """Update conda environment"""
    print("🐍 Updating conda environment...")
    try:
        subprocess.run(['conda', 'env', 'update', '-f', 'environment.yml'], check=True)
        print("✅ Conda environment updated successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update conda environment: {e}")
    except FileNotFoundError:
        print("⚠️  conda not found in PATH")

if __name__ == "__main__":
    sys.exit(main())
```

### Task 2: Virtual Environment Management

Extend the hook to handle Python virtual environments per branch.

```python
#!/usr/bin/env python3
"""
Advanced post-checkout hook with virtual environment management
"""
import sys
import os
import subprocess
import json
from pathlib import Path

class VirtualEnvManager:
    def __init__(self):
        self.venv_dir = Path('.venvs')
        self.venv_dir.mkdir(exist_ok=True)
    
    def get_branch_name(self):
        """Get current branch name"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_venv_path(self, branch_name):
        """Get virtual environment path for branch"""
        safe_branch = branch_name.replace('/', '_').replace('-', '_')
        return self.venv_dir / f"venv_{safe_branch}"
    
    def create_or_activate_venv(self, branch_name):
        """Create or activate virtual environment for branch"""
        venv_path = self.get_venv_path(branch_name)
        
        if not venv_path.exists():
            print(f"🐍 Creating virtual environment for branch: {branch_name}")
            try:
                subprocess.run(['python', '-m', 'venv', str(venv_path)], check=True)
                print(f"✅ Virtual environment created: {venv_path}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create virtual environment: {e}")
                return False
        
        # Create activation script
        self.create_activation_script(branch_name, venv_path)
        return True
    
    def create_activation_script(self, branch_name, venv_path):
        """Create a script to activate the virtual environment"""
        activate_script = Path('.activate_venv.sh')
        
        script_content = f"""#!/bin/bash
# Auto-generated activation script for branch: {branch_name}
echo "🐍 Activating virtual environment for branch: {branch_name}"
source {venv_path}/bin/activate
echo "✅ Virtual environment activated: {venv_path}"
echo "💡 Run 'deactivate' to exit the virtual environment"
"""
        
        with open(activate_script, 'w') as f:
            f.write(script_content)
        
        os.chmod(activate_script, 0o755)
        
        print(f"📝 Activation script created: {activate_script}")
        print(f"💡 Run 'source .activate_venv.sh' to activate the environment")

class DependencyManager:
    def __init__(self, venv_manager):
        self.venv_manager = venv_manager
    
    def detect_dependency_files(self):
        """Detect which dependency files exist"""
        files = {
            'requirements.txt': Path('requirements.txt').exists(),
            'requirements-dev.txt': Path('requirements-dev.txt').exists(),
            'package.json': Path('package.json').exists(),
            'Pipfile': Path('Pipfile').exists(),
            'pyproject.toml': Path('pyproject.toml').exists(),
            'environment.yml': Path('environment.yml').exists(),
        }
        return {k: v for k, v in files.items() if v}
    
    def install_all_dependencies(self, branch_name):
        """Install all detected dependencies"""
        dependency_files = self.detect_dependency_files()
        
        if not dependency_files:
            print("ℹ️  No dependency files found")
            return
        
        print(f"📦 Installing dependencies for branch: {branch_name}")
        
        # Get virtual environment path
        venv_path = self.venv_manager.get_venv_path(branch_name)
        pip_path = venv_path / 'bin' / 'pip'
        
        # Install Python dependencies in virtual environment
        if dependency_files.get('requirements.txt'):
            self.install_with_pip(pip_path, 'requirements.txt')
        
        if dependency_files.get('requirements-dev.txt'):
            self.install_with_pip(pip_path, 'requirements-dev.txt')
        
        # Install other dependencies
        if dependency_files.get('package.json'):
            self.install_npm()
        
        if dependency_files.get('Pipfile'):
            print("⚠️  Pipfile detected but using venv instead of pipenv")
    
    def install_with_pip(self, pip_path, requirements_file):
        """Install pip requirements in virtual environment"""
        print(f"🐍 Installing {requirements_file} in virtual environment...")
        try:
            subprocess.run([str(pip_path), 'install', '-r', requirements_file], 
                          check=True)
            print(f"✅ {requirements_file} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {requirements_file}: {e}")
        except FileNotFoundError:
            print(f"⚠️  pip not found at {pip_path}")
    
    def install_npm(self):
        """Install npm dependencies"""
        print("📦 Installing npm dependencies...")
        try:
            subprocess.run(['npm', 'install'], check=True)
            print("✅ npm dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install npm dependencies: {e}")
        except FileNotFoundError:
            print("⚠️  npm not found in PATH")

def main():
    if len(sys.argv) != 4:
        return 0
    
    prev_head = sys.argv[1]
    new_head = sys.argv[2]
    branch_checkout = sys.argv[3] == '1'
    
    if not branch_checkout:
        return 0
    
    print("🔄 Advanced Post-checkout Hook")
    print("=" * 40)
    
    # Initialize managers
    venv_manager = VirtualEnvManager()
    dep_manager = DependencyManager(venv_manager)
    
    # Get current branch
    branch_name = venv_manager.get_branch_name()
    if not branch_name:
        print("❌ Could not determine branch name")
        return 1
    
    print(f"🌿 Switched to branch: {branch_name}")
    
    # Create/activate virtual environment
    if venv_manager.create_or_activate_venv(branch_name):
        # Install dependencies
        dep_manager.install_all_dependencies(branch_name)
    
    print("✅ Post-checkout setup complete!")
    print("💡 Remember to activate your virtual environment:")
    print("   source .activate_venv.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Task 3: Configuration-Driven Dependencies

Create a configuration system for branch-specific dependencies.

```python
# Create .checkout-config.json
{
  "virtual_environments": {
    "enabled": true,
    "base_dir": ".venvs",
    "python_version": "python3"
  },
  "dependencies": {
    "auto_install": true,
    "install_dev_deps": true
  },
  "branch_configs": {
    "main": {
      "requirements": ["requirements.txt"],
      "pre_install": ["pip install --upgrade pip"],
      "post_install": ["echo 'Main branch setup complete'"]
    },
    "develop": {
      "requirements": ["requirements.txt", "requirements-dev.txt"],
      "pre_install": ["pip install --upgrade pip setuptools"],
      "post_install": ["pre-commit install"]
    },
    "feature/*": {
      "requirements": ["requirements.txt", "requirements-dev.txt"],
      "pre_install": ["pip install --upgrade pip"],
      "post_install": []
    }
  }
}
```

## Key Concepts

### Post-Checkout Hook
- **Timing**: Runs after successful checkout
- **Parameters**: previous HEAD, new HEAD, branch flag
- **Use Cases**: Environment setup, dependency installation
- **Non-blocking**: Cannot prevent checkout (already happened)

### Virtual Environment Management
- **Branch Isolation**: Each branch gets its own environment
- **Dependency Isolation**: Prevent version conflicts
- **Automatic Activation**: Scripts to make switching easy

### Dependency Detection
- **File Monitoring**: Watch for changes in dependency files
- **Multiple Managers**: Support pip, npm, conda, etc.
- **Smart Installation**: Only install what changed

## Best Practices

1. **Fast Execution**: Don't slow down branch switching
2. **Error Handling**: Continue even if some deps fail
3. **User Feedback**: Show what's happening
4. **Configurability**: Make behavior customizable
5. **Cleanup**: Remove old environments periodically

## Next Steps

Lab 6 introduces the pre-commit framework for professional-grade hook management.

## Summary

You've learned to automate development environment setup with post-checkout hooks, ensuring dependencies are always current when switching branches.