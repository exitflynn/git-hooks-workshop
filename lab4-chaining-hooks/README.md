# Lab 4: Chaining Hooks & Branch-Specific Logic

## Learning Objectives
- Chain multiple hook types together for complete validation
- Implement branch-specific rules and policies
- Create a hook orchestration system
- Learn about Git branch detection in hooks
- Build configurable branch-based workflows

## Overview

In this lab, you'll learn how to create sophisticated Git workflows by chaining multiple hooks together and applying different rules based on the target branch. This is essential for implementing different policies for feature branches, main branches, and release branches.

## Setup

1. Create a new directory for this lab:
   ```bash
   mkdir lab4-practice
   cd lab4-practice
   git init
   git config user.email "test@example.com"
   git config user.name "Test User"
   ```

2. Create multiple branches to test with:
   ```bash
   # Create and switch to main branch
   git checkout -b main
   echo "# Project" > README.md
   git add README.md
   git commit -m "Initial commit"
   
   # Create feature branch
   git checkout -b feature/user-auth
   
   # Create development branch
   git checkout -b develop
   
   # Create release branch
   git checkout -b release/v1.0.0
   ```

## Tasks

### Task 1: Branch Detection Utility

Create a utility that can detect the current branch and target branch for different Git operations.

1. Create a branch utility script:
   ```bash
   mkdir .git/hook-utils
   touch .git/hook-utils/branch_utils.py
   chmod +x .git/hook-utils/branch_utils.py
   ```

2. Implement branch detection:
   ```python
   #!/usr/bin/env python3
   """
   Utility functions for Git branch operations in hooks
   """
   import subprocess
   import sys
   import re
   
   class BranchInfo:
       def __init__(self):
           self.current_branch = self.get_current_branch()
           self.target_branch = None
           self.is_merge = False
           self.source_branch = None
       
       def get_current_branch(self):
           """Get the current branch name"""
           try:
               result = subprocess.run(['git', 'branch', '--show-current'], 
                                     capture_output=True, text=True, check=True)
               return result.stdout.strip()
           except subprocess.CalledProcessError:
               return None
       
       def get_target_branch_from_push(self, ref_name):
           """Extract target branch from push ref (used in pre-push hook)"""
           # ref_name format: refs/heads/branch-name
           if ref_name.startswith('refs/heads/'):
               return ref_name[11:]  # Remove 'refs/heads/'
           return ref_name
       
       def detect_merge_info(self, commit_msg=None):
           """Detect if this is a merge operation and extract branch info"""
           if commit_msg:
               # Check for merge commit message patterns
               merge_patterns = [
                   r"Merge branch '([^']+)'",
                   r"Merge pull request #\d+ from ([^/]+)/([^/\s]+)",
                   r"Merge remote-tracking branch '([^']+)'"
               ]
               
               for pattern in merge_patterns:
                   match = re.search(pattern, commit_msg)
                   if match:
                       self.is_merge = True
                       self.source_branch = match.group(1)
                       return True
           
           return False
       
       def is_protected_branch(self, branch_name):
           """Check if a branch is protected"""
           protected_branches = ['main', 'master', 'production', 'release']
           return any(branch_name.startswith(protected) or branch_name == protected 
                     for protected in protected_branches)
       
       def get_branch_type(self, branch_name):
           """Determine branch type based on naming convention"""
           if not branch_name:
               return 'unknown'
           
           branch_patterns = {
               'main': r'^(main|master)$',
               'develop': r'^develop$',
               'feature': r'^feature/',
               'bugfix': r'^(bugfix|fix)/',
               'hotfix': r'^hotfix/',
               'release': r'^release/',
               'experimental': r'^(experimental|exp)/',
           }
           
           for branch_type, pattern in branch_patterns.items():
               if re.match(pattern, branch_name):
                   return branch_type
           
           return 'other'
       
       def get_merge_target(self):
           """Get the target branch for merge operations"""
           try:
               # Try to get merge target from git status
               result = subprocess.run(['git', 'status', '--porcelain=v1'], 
                                     capture_output=True, text=True, check=True)
               
               # Look for merge in progress
               if 'UU' in result.stdout or 'AA' in result.stdout:
                   # There's a merge conflict, try to get target from MERGE_HEAD
                   try:
                       with open('.git/MERGE_HEAD', 'r') as f:
                           merge_head = f.read().strip()
                       
                       # Get branch name from merge head
                       result = subprocess.run(['git', 'name-rev', '--name-only', merge_head], 
                                             capture_output=True, text=True, check=True)
                       return result.stdout.strip()
                   except (IOError, subprocess.CalledProcessError):
                       pass
               
               return None
           except subprocess.CalledProcessError:
               return None
   
   def get_branch_config(branch_name):
       """Get configuration for a specific branch type"""
       branch_type = BranchInfo().get_branch_type(branch_name)
       
       configs = {
           'main': {
               'require_review': True,
               'require_tests': True,
               'require_conventional_commits': True,
               'require_jira': True,
               'allow_direct_push': False,
               'max_commit_size': 5
           },
           'develop': {
               'require_review': False,
               'require_tests': True,
               'require_conventional_commits': True,
               'require_jira': True,
               'allow_direct_push': True,
               'max_commit_size': 10
           },
           'feature': {
               'require_review': False,
               'require_tests': False,
               'require_conventional_commits': False,
               'require_jira': True,
               'allow_direct_push': True,
               'max_commit_size': 20
           },
           'release': {
               'require_review': True,
               'require_tests': True,
               'require_conventional_commits': True,
               'require_jira': True,
               'allow_direct_push': False,
               'max_commit_size': 3
           },
           'hotfix': {
               'require_review': True,
               'require_tests': True,
               'require_conventional_commits': False,
               'require_jira': True,
               'allow_direct_push': True,
               'max_commit_size': 1
           }
       }
       
       return configs.get(branch_type, configs['feature'])  # Default to feature config
   
   if __name__ == "__main__":
       # Test the utilities
       branch_info = BranchInfo()
       print(f"Current branch: {branch_info.current_branch}")
       print(f"Branch type: {branch_info.get_branch_type(branch_info.current_branch)}")
       print(f"Is protected: {branch_info.is_protected_branch(branch_info.current_branch)}")
       
       config = get_branch_config(branch_info.current_branch)
       print(f"Branch config: {config}")
   ```

### Task 2: Hook Orchestrator

Create a system that runs multiple validations based on the branch and operation type.

1. Create the hook orchestrator:
   ```bash
   touch .git/hook-utils/hook_orchestrator.py
   chmod +x .git/hook-utils/hook_orchestrator.py
   ```

2. Implement the orchestrator:
   ```python
   #!/usr/bin/env python3
   """
   Hook orchestrator that manages multiple validation steps
   """
   import sys
   import os
   import importlib.util
   import subprocess
   from pathlib import Path
   
   # Add hook-utils to path
   sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
   from branch_utils import BranchInfo, get_branch_config
   
   class ValidationResult:
       def __init__(self, success=True, message="", warning=False):
           self.success = success
           self.message = message
           self.warning = warning
   
   class HookOrchestrator:
       def __init__(self, hook_type):
           self.hook_type = hook_type
           self.branch_info = BranchInfo()
           self.config = get_branch_config(self.branch_info.current_branch)
           self.validators = []
           self.results = []
       
       def add_validator(self, validator_func, name, required=True):
           """Add a validation function to the orchestrator"""
           self.validators.append({
               'func': validator_func,
               'name': name,
               'required': required
           })
       
       def run_validation(self, *args, **kwargs):
           """Run all validations and collect results"""
           print(f"🔄 Running {self.hook_type} validations for branch: {self.branch_info.current_branch}")
           print(f"📋 Branch type: {self.branch_info.get_branch_type(self.branch_info.current_branch)}")
           print("=" * 50)
           
           all_success = True
           has_warnings = False
           
           for validator in self.validators:
               print(f"\n🔍 {validator['name']}...")
               
               try:
                   result = validator['func'](*args, **kwargs)
                   
                   if isinstance(result, ValidationResult):
                       self.results.append(result)
                   else:
                       # Convert boolean or tuple to ValidationResult
                       if isinstance(result, tuple):
                           success, message = result
                           result = ValidationResult(success, message)
                       else:
                           result = ValidationResult(result, "")
                       self.results.append(result)
                   
                   if result.success:
                       print(f"   ✅ {result.message or 'Passed'}")
                   elif result.warning:
                       print(f"   ⚠️  {result.message}")
                       has_warnings = True
                   else:
                       print(f"   ❌ {result.message}")
                       if validator['required']:
                           all_success = False
               
               except Exception as e:
                   error_result = ValidationResult(False, f"Validation error: {e}")
                   self.results.append(error_result)
                   print(f"   💥 Error: {e}")
                   if validator['required']:
                       all_success = False
           
           # Summary
           print(f"\n📊 Validation Summary:")
           passed = sum(1 for r in self.results if r.success)
           warnings = sum(1 for r in self.results if r.warning)
           failed = sum(1 for r in self.results if not r.success and not r.warning)
           
           print(f"   ✅ Passed: {passed}")
           if warnings > 0:
               print(f"   ⚠️  Warnings: {warnings}")
           if failed > 0:
               print(f"   ❌ Failed: {failed}")
           
           if all_success:
               if has_warnings:
                   print("✅ All required validations passed (with warnings)")
               else:
                   print("✅ All validations passed!")
               return 0
           else:
               print("❌ Some required validations failed")
               return 1
   
   # Individual validation functions
   def validate_branch_protection(branch_info, config):
       """Check if direct pushes to protected branches are allowed"""
       if branch_info.is_protected_branch(branch_info.current_branch):
           if not config.get('allow_direct_push', False):
               return ValidationResult(
                   False, 
                   f"Direct pushes to protected branch '{branch_info.current_branch}' are not allowed"
               )
       
       return ValidationResult(True, "Branch protection check passed")
   
   def validate_commit_count(config):
       """Check if the number of commits being pushed is within limits"""
       try:
           # Get number of commits ahead of origin
           result = subprocess.run(['git', 'rev-list', '--count', 'HEAD', '^origin/HEAD'], 
                                 capture_output=True, text=True)
           
           if result.returncode == 0:
               commit_count = int(result.stdout.strip())
               max_commits = config.get('max_commit_size', 10)
               
               if commit_count > max_commits:
                   return ValidationResult(
                       False, 
                       f"Too many commits ({commit_count} > {max_commits}). Consider squashing."
                   )
               
               return ValidationResult(True, f"Commit count OK ({commit_count} commits)")
           else:
               return ValidationResult(True, "Unable to check commit count (no remote)")
       
       except Exception as e:
           return ValidationResult(True, f"Commit count check skipped: {e}", warning=True)
   
   def validate_conventional_commits(config):
       """Validate conventional commit format if required"""
       if not config.get('require_conventional_commits', False):
           return ValidationResult(True, "Conventional commits not required")
       
       try:
           # Get commits to be pushed
           result = subprocess.run(['git', 'log', '--oneline', 'HEAD', '^origin/HEAD'], 
                                 capture_output=True, text=True)
           
           if result.returncode == 0:
               commits = result.stdout.strip().split('\n')
               conventional_pattern = r'^[a-f0-9]+ (feat|fix|docs|style|refactor|perf|test|chore|build|ci)(\([^)]+\))?!?:'
               
               for commit in commits:
                   if commit.strip():
                       import re
                       if not re.match(conventional_pattern, commit):
                           return ValidationResult(
                               False, 
                               f"Non-conventional commit found: {commit[:50]}..."
                           )
               
               return ValidationResult(True, "All commits follow conventional format")
           else:
               return ValidationResult(True, "No commits to validate")
       
       except Exception as e:
           return ValidationResult(True, f"Conventional commit check skipped: {e}", warning=True)
   
   def validate_jira_tickets(config):
       """Validate Jira ticket references if required"""
       if not config.get('require_jira', False):
           return ValidationResult(True, "Jira tickets not required")
       
       try:
           # Get commits to be pushed
           result = subprocess.run(['git', 'log', '--oneline', 'HEAD', '^origin/HEAD'], 
                                 capture_output=True, text=True)
           
           if result.returncode == 0:
               commits = result.stdout.strip().split('\n')
               jira_pattern = r'[A-Z]{2,}-\d+'
               
               for commit in commits:
                   if commit.strip():
                       import re
                       if not re.search(jira_pattern, commit):
                           return ValidationResult(
                               False, 
                               f"Missing Jira ticket in commit: {commit[:50]}..."
                           )
               
               return ValidationResult(True, "All commits have Jira tickets")
           else:
               return ValidationResult(True, "No commits to validate")
       
       except Exception as e:
           return ValidationResult(True, f"Jira ticket check skipped: {e}", warning=True)
   
   def validate_tests(config):
       """Run tests if required"""
       if not config.get('require_tests', False):
           return ValidationResult(True, "Tests not required")
       
       # Check if test files exist
       test_files = list(Path('.').glob('test_*.py')) + list(Path('.').glob('*_test.py'))
       if not test_files:
           return ValidationResult(True, "No test files found", warning=True)
       
       try:
           # Run python tests
           result = subprocess.run(['python', '-m', 'pytest', '--tb=short'], 
                                 capture_output=True, text=True, timeout=30)
           
           if result.returncode == 0:
               return ValidationResult(True, "All tests passed")
           else:
               return ValidationResult(False, f"Tests failed: {result.stdout[-200:]}")
       
       except subprocess.TimeoutExpired:
           return ValidationResult(False, "Tests timed out")
       except FileNotFoundError:
           # pytest not available, try basic python syntax check
           return ValidationResult(True, "pytest not available, skipping tests", warning=True)
       except Exception as e:
           return ValidationResult(True, f"Test execution error: {e}", warning=True)
   
   if __name__ == "__main__":
       # Example usage
       orchestrator = HookOrchestrator("pre-push")
       
       # Add validations based on config
       orchestrator.add_validator(
           lambda: validate_branch_protection(orchestrator.branch_info, orchestrator.config),
           "Branch Protection"
       )
       orchestrator.add_validator(
           lambda: validate_commit_count(orchestrator.config),
           "Commit Count"
       )
       orchestrator.add_validator(
           lambda: validate_conventional_commits(orchestrator.config),
           "Conventional Commits"
       )
       orchestrator.add_validator(
           lambda: validate_jira_tickets(orchestrator.config),
           "Jira Tickets"
       )
       orchestrator.add_validator(
           lambda: validate_tests(orchestrator.config),
           "Tests",
           required=False  # Make tests optional
       )
       
       # Run validations
       exit_code = orchestrator.run_validation()
       sys.exit(exit_code)
   ```

### Task 3: Chained Pre-commit Hook

Create a pre-commit hook that uses the orchestrator to run different validations based on the branch.

1. Create the pre-commit hook:
   ```bash
   touch .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. Implement the chained pre-commit hook:
   ```python
   #!/usr/bin/env python3
   """
   Chained pre-commit hook with branch-specific logic
   """
   import sys
   import os
   import subprocess
   import ast
   import re
   
   # Add hook-utils to path
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hook-utils'))
   from hook_orchestrator import HookOrchestrator, ValidationResult
   from branch_utils import BranchInfo, get_branch_config
   
   def validate_python_syntax():
       """Validate Python file syntax"""
       try:
           result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                 capture_output=True, text=True, check=True)
           
           python_files = [f for f in result.stdout.strip().split('\n') 
                          if f.endswith('.py') and f]
           
           if not python_files:
               return ValidationResult(True, "No Python files to check")
           
           errors = []
           for filename in python_files:
               try:
                   with open(filename, 'r') as f:
                       ast.parse(f.read())
               except SyntaxError as e:
                   errors.append(f"{filename}: Line {e.lineno}: {e.msg}")
               except Exception as e:
                   errors.append(f"{filename}: {e}")
           
           if errors:
               return ValidationResult(False, f"Python syntax errors: {'; '.join(errors)}")
           
           return ValidationResult(True, f"Python syntax OK ({len(python_files)} files)")
       
       except Exception as e:
           return ValidationResult(True, f"Python syntax check skipped: {e}", warning=True)
   
   def validate_file_size():
       """Check for large files being committed"""
       try:
           result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                 capture_output=True, text=True, check=True)
           
           large_files = []
           max_size = 1024 * 1024  # 1MB
           
           for filename in result.stdout.strip().split('\n'):
               if filename and os.path.exists(filename):
                   size = os.path.getsize(filename)
                   if size > max_size:
                       large_files.append(f"{filename} ({size // 1024}KB)")
           
           if large_files:
               return ValidationResult(
                   False, 
                   f"Large files detected: {', '.join(large_files)}. Consider Git LFS."
               )
           
           return ValidationResult(True, "No large files detected")
       
       except Exception as e:
           return ValidationResult(True, f"File size check skipped: {e}", warning=True)
   
   def validate_commit_message_preview():
       """Preview commit message requirements for this branch"""
       branch_info = BranchInfo()
       config = get_branch_config(branch_info.current_branch)
       
       requirements = []
       if config.get('require_jira'):
           requirements.append("Jira ticket reference")
       if config.get('require_conventional_commits'):
           requirements.append("Conventional commit format")
       
       if requirements:
           message = f"Reminder: This branch requires {', '.join(requirements)}"
           return ValidationResult(True, message, warning=True)
       
       return ValidationResult(True, "No special commit message requirements")
   
   def validate_no_debug_code():
       """Check for debug code in staged files"""
       try:
           result = subprocess.run(['git', 'diff', '--cached'], 
                                 capture_output=True, text=True, check=True)
           
           debug_patterns = [
               r'console\.log\(',
               r'print\(',
               r'debugger;',
               r'pdb\.set_trace\(',
               r'import pdb',
               r'// TODO:',
               r'# TODO:',
               r'FIXME',
           ]
           
           debug_lines = []
           for i, line in enumerate(result.stdout.split('\n'), 1):
               if line.startswith('+'):  # Added line
                   for pattern in debug_patterns:
                       if re.search(pattern, line, re.IGNORECASE):
                           debug_lines.append(f"Line {i}: {line.strip()[:50]}")
           
           if debug_lines:
               return ValidationResult(
                   False,
                   f"Debug code detected: {'; '.join(debug_lines[:3])}"
               )
           
           return ValidationResult(True, "No debug code detected")
       
       except Exception as e:
           return ValidationResult(True, f"Debug code check skipped: {e}", warning=True)
   
   def main():
       print("🔗 Chained Pre-commit Hook")
       print("=" * 30)
       
       # Create orchestrator
       orchestrator = HookOrchestrator("pre-commit")
       
       # Always run basic validations
       orchestrator.add_validator(validate_python_syntax, "Python Syntax")
       orchestrator.add_validator(validate_file_size, "File Size")
       orchestrator.add_validator(validate_no_debug_code, "Debug Code Check")
       
       # Add branch-specific reminder
       orchestrator.add_validator(validate_commit_message_preview, "Commit Message Requirements", required=False)
       
       # Run all validations
       return orchestrator.run_validation()
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

### Task 4: Branch-Aware Pre-push Hook

Create a pre-push hook that enforces different policies based on the target branch.

1. Create the pre-push hook:
   ```bash
   touch .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

2. Implement the branch-aware pre-push hook:
   ```python
   #!/usr/bin/env python3
   """
   Branch-aware pre-push hook
   """
   import sys
   import os
   import subprocess
   
   # Add hook-utils to path
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hook-utils'))
   from hook_orchestrator import HookOrchestrator, ValidationResult
   from branch_utils import BranchInfo, get_branch_config
   
   def validate_push_permissions(remote_name, remote_url, local_ref, remote_ref):
       """Validate push permissions based on branch and user"""
       branch_info = BranchInfo()
       target_branch = branch_info.get_target_branch_from_push(remote_ref)
       
       # Get config for target branch
       config = get_branch_config(target_branch)
       
       # Check if direct push is allowed
       if branch_info.is_protected_branch(target_branch):
           if not config.get('allow_direct_push', False):
               return ValidationResult(
                   False,
                   f"Direct push to protected branch '{target_branch}' is not allowed. Use pull request."
               )
       
       return ValidationResult(True, f"Push to '{target_branch}' is allowed")
   
   def validate_ahead_behind_status(remote_name, remote_url, local_ref, remote_ref):
       """Check if local branch is behind remote"""
       try:
           # Fetch latest from remote
           subprocess.run(['git', 'fetch', remote_name], 
                         capture_output=True, check=True)
           
           # Check if we're behind
           result = subprocess.run(['git', 'rev-list', '--count', f'{local_ref}..{remote_ref}'], 
                                 capture_output=True, text=True)
           
           if result.returncode == 0:
               behind_count = int(result.stdout.strip())
               if behind_count > 0:
                   return ValidationResult(
                       False,
                       f"Local branch is {behind_count} commits behind remote. Please pull first."
                   )
           
           return ValidationResult(True, "Branch is up to date with remote")
       
       except Exception as e:
           return ValidationResult(True, f"Unable to check remote status: {e}", warning=True)
   
   def validate_force_push(local_ref, remote_ref):
       """Detect and validate force pushes"""
       try:
           # Check if this would be a force push
           result = subprocess.run(['git', 'merge-base', '--is-ancestor', remote_ref, local_ref], 
                                 capture_output=True)
           
           if result.returncode != 0:
               # This is a force push
               branch_info = BranchInfo()
               target_branch = branch_info.get_target_branch_from_push(remote_ref)
               
               if branch_info.is_protected_branch(target_branch):
                   return ValidationResult(
                       False,
                       f"Force push to protected branch '{target_branch}' is not allowed"
                   )
               else:
                   return ValidationResult(
                       True,
                       f"Force push to '{target_branch}' detected but allowed",
                       warning=True
                   )
           
           return ValidationResult(True, "Fast-forward push")
       
       except Exception as e:
           return ValidationResult(True, f"Force push check skipped: {e}", warning=True)
   
   def validate_commit_history(local_ref, remote_ref):
       """Validate commit history before push"""
       try:
           # Get commits to be pushed
           result = subprocess.run(['git', 'rev-list', f'{remote_ref}..{local_ref}'], 
                                 capture_output=True, text=True, check=True)
           
           commit_hashes = result.stdout.strip().split('\n')
           if not commit_hashes or commit_hashes == ['']:
               return ValidationResult(True, "No new commits to push")
           
           # Validate each commit
           invalid_commits = []
           for commit_hash in commit_hashes:
               if commit_hash:
                   # Get commit message
                   msg_result = subprocess.run(['git', 'log', '-1', '--pretty=format:%s', commit_hash], 
                                             capture_output=True, text=True, check=True)
                   commit_msg = msg_result.stdout.strip()
                   
                   # Check for invalid commit messages
                   if len(commit_msg) < 10:
                       invalid_commits.append(f"{commit_hash[:8]}: Message too short")
                   elif commit_msg.lower().startswith('wip'):
                       invalid_commits.append(f"{commit_hash[:8]}: WIP commit should be squashed")
           
           if invalid_commits:
               return ValidationResult(
                   False,
                   f"Invalid commits found: {'; '.join(invalid_commits[:2])}"
               )
           
           return ValidationResult(True, f"All {len(commit_hashes)} commits are valid")
       
       except Exception as e:
           return ValidationResult(True, f"Commit history check skipped: {e}", warning=True)
   
   def main():
       # Parse pre-push hook arguments
       if len(sys.argv) < 3:
           print("Error: pre-push hook requires remote name and URL")
           sys.exit(1)
       
       remote_name = sys.argv[1]
       remote_url = sys.argv[2]
       
       print(f"🚀 Pre-push Hook: {remote_name} ({remote_url})")
       print("=" * 50)
       
       # Read refs from stdin
       local_ref = None
       remote_ref = None
       
       for line in sys.stdin:
           parts = line.strip().split()
           if len(parts) >= 4:
               local_ref = parts[1]
               remote_ref = parts[3]
               break
       
       if not local_ref or not remote_ref:
           print("No refs to push")
           return 0
       
       print(f"📤 Pushing {local_ref} -> {remote_ref}")
       
       # Create orchestrator
       orchestrator = HookOrchestrator("pre-push")
       
       # Add validations
       orchestrator.add_validator(
           lambda: validate_push_permissions(remote_name, remote_url, local_ref, remote_ref),
           "Push Permissions"
       )
       
       orchestrator.add_validator(
           lambda: validate_ahead_behind_status(remote_name, remote_url, local_ref, remote_ref),
           "Branch Status"
       )
       
       orchestrator.add_validator(
           lambda: validate_force_push(local_ref, remote_ref),
           "Force Push Check"
       )
       
       orchestrator.add_validator(
           lambda: validate_commit_history(local_ref, remote_ref),
           "Commit History"
       )
       
       # Run branch-specific validations from orchestrator
       branch_info = BranchInfo()
       target_branch = branch_info.get_target_branch_from_push(remote_ref)
       config = get_branch_config(target_branch)
       
       # Import additional validators
       from hook_orchestrator import validate_conventional_commits, validate_jira_tickets
       
       if config.get('require_conventional_commits'):
           orchestrator.add_validator(
               lambda: validate_conventional_commits(config),
               "Conventional Commits"
           )
       
       if config.get('require_jira'):
           orchestrator.add_validator(
               lambda: validate_jira_tickets(config),
               "Jira Tickets"
           )
       
       # Run all validations
       return orchestrator.run_validation()
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

### Task 5: Test the Chained Hooks

Test your hook chain with different branches and scenarios.

1. Test on different branches:
   ```bash
   # Test on feature branch (should be lenient)
   git checkout feature/user-auth
   echo "def test_feature(): pass" > feature.py
   git add feature.py
   git commit -m "Add feature code"
   
   # Test on main branch (should be strict)
   git checkout main
   echo "def main_feature(): pass" > main.py
   git add main.py
   git commit -m "PROJ-123: Add main feature"  # Should require Jira
   
   # Test on release branch (should be very strict)
   git checkout release/v1.0.0
   echo "def release_fix(): pass" > release.py
   git add release.py
   git commit -m "fix: PROJ-456 critical bug in release"
   ```

2. Test push restrictions:
   ```bash
   # Try to push to different branches
   git push origin feature/user-auth  # Should work
   git push origin main  # May be restricted based on config
   ```

## Key Concepts

### Hook Chaining Benefits

1. **Modular Validation**: Each validator handles one concern
2. **Branch-Specific Logic**: Different rules for different branch types
3. **Configurable Policies**: Easy to adjust rules per project
4. **Clear Feedback**: Users understand exactly what failed

### Branch-Based Workflows

1. **Feature Branches**: Relaxed rules, focus on development
2. **Main/Master**: Strict rules, require review and testing
3. **Release Branches**: Very strict, minimal changes allowed
4. **Hotfix Branches**: Fast-track but still validated

### Hook Orchestration Patterns

1. **Validator Functions**: Pure functions that return results
2. **Configuration-Driven**: Rules defined in config, not code
3. **Error Aggregation**: Collect all errors before failing
4. **Graceful Degradation**: Continue when non-critical checks fail

### Branch Detection Strategies

1. **Current Branch**: `git branch --show-current`
2. **Target Branch**: Parse from push refs or merge info
3. **Branch Type**: Pattern matching on branch names
4. **Protection Status**: Check against protected branch list

## Troubleshooting

### Hook Utils Not Found?
```bash
# Ensure hook-utils directory exists and has proper files
ls -la .git/hook-utils/
# Check Python path in hooks
```

### Branch Detection Failing?
```bash
# Test branch utilities manually
python3 .git/hook-utils/branch_utils.py
```

### Validation Errors?
- Check individual validator functions
- Test with simple cases first
- Add debug output to orchestrator

## Best Practices

1. **Start Simple**: Begin with basic validations, add complexity gradually
2. **Make It Configurable**: Use config files for branch-specific rules
3. **Provide Clear Feedback**: Tell users exactly what's wrong and how to fix it
4. **Handle Errors Gracefully**: Don't crash on unexpected conditions
5. **Performance Matters**: Keep validations fast, especially for large repositories

## Next Steps

In Lab 5, you'll learn how to automatically install dependencies when switching branches using the post-checkout hook.

## Summary

You've learned:
- How to chain multiple hook types together
- How to implement branch-specific validation logic
- How to create a hook orchestration system
- How to detect branch information in different Git operations
- How to build configurable, maintainable hook workflows

Your Git workflow now automatically adapts to different branch types and enforces appropriate policies!