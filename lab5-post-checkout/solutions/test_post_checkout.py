#!/usr/bin/env python3
"""
Test script for post-checkout hook functionality.
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

def create_test_repo():
    """Create a temporary git repository for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=temp_dir, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir)
    
    # Create test files
    (temp_dir / 'requirements.txt').write_text('requests==2.28.0\npytest==7.0.0\n')
    (temp_dir / 'README.md').write_text('# Test Repository\n')
    
    # Create initial commit
    subprocess.run(['git', 'add', '.'], cwd=temp_dir)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=temp_dir)
    
    # Create and switch to feature branch
    subprocess.run(['git', 'checkout', '-b', 'feature/test'], cwd=temp_dir)
    
    # Add different requirements for feature branch
    (temp_dir / 'dev-requirements.txt').write_text('black==22.0.0\nflake8==4.0.0\n')
    subprocess.run(['git', 'add', 'dev-requirements.txt'], cwd=temp_dir)
    subprocess.run(['git', 'commit', '-m', 'Add dev requirements'], cwd=temp_dir)
    
    return temp_dir

def test_post_checkout_hook(test_repo, hook_path):
    """Test the post-checkout hook."""
    # Copy hook to test repository
    hooks_dir = test_repo / '.git' / 'hooks'
    hook_dest = hooks_dir / 'post-checkout'
    
    shutil.copy2(hook_path, hook_dest)
    os.chmod(hook_dest, 0o755)
    
    # Copy config file if it exists
    config_path = hook_path.parent / '.post-checkout-config'
    if config_path.exists():
        shutil.copy2(config_path, test_repo / '.post-checkout-config')
    
    print(f"Testing post-checkout hook in {test_repo}")
    
    # Switch back to main branch (should trigger hook)
    try:
        result = subprocess.run(
            ['git', 'checkout', 'main'],
            cwd=test_repo,
            capture_output=True,
            text=True
        )
        print("Git checkout output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"Git checkout failed: {e}")
    
    # Switch back to feature branch
    try:
        result = subprocess.run(
            ['git', 'checkout', 'feature/test'],
            cwd=test_repo,
            capture_output=True,
            text=True
        )
        print("\nSwitching to feature branch:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"Git checkout failed: {e}")

def main():
    """Test post-checkout hooks."""
    script_dir = Path(__file__).parent
    
    # Test the main hook
    main_hook = script_dir / 'post-checkout'
    simple_hook = script_dir / 'post-checkout-simple'
    
    if main_hook.exists():
        print("=== Testing main post-checkout hook ===")
        test_repo = create_test_repo()
        try:
            test_post_checkout_hook(test_repo, main_hook)
        finally:
            shutil.rmtree(test_repo)
        
        print("\n" + "="*50 + "\n")
    
    if simple_hook.exists():
        print("=== Testing simple post-checkout hook ===")
        test_repo = create_test_repo()
        try:
            test_post_checkout_hook(test_repo, simple_hook)
        finally:
            shutil.rmtree(test_repo)

if __name__ == '__main__':
    main()