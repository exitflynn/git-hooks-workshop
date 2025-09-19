# Lab 1 Solutions

## Complete Solution Scripts

### Task 1: Hello World Pre-commit Hook
```python
#!/usr/bin/env python3

print("🚀 Hello from your custom pre-commit hook!")
print("📝 Running pre-commit checks...")

# Exit with 0 to allow the commit to proceed
exit(0)
```

### Task 2: Blocking Hook
```python
#!/usr/bin/env python3

print("🚀 Hello from your custom pre-commit hook!")
print("❌ This hook will block your commit!")

# Exit with 1 to block the commit
exit(1)
```

### Task 3: Conditional Hook (Day-based)
```python
#!/usr/bin/env python3
import datetime

today = datetime.datetime.now()
day_of_week = today.strftime("%A")

print(f"🗓️  Today is {day_of_week}")

if day_of_week == "Friday":
    print("🎉 It's Friday! No commits allowed - time to celebrate!")
    print("💡 Use --no-verify to bypass this check if needed")
    exit(1)
else:
    print("✅ Weekday commit approved!")
    exit(0)
```

### Task 4: Interactive Hook
```python
#!/usr/bin/env python3
import sys
import subprocess

print("🤔 Are you sure you want to commit these changes?")
print("📋 Staged files:")

# Show staged files
try:
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                           capture_output=True, text=True, check=True)
    
    staged_files = result.stdout.strip().split('\n')
    for file in staged_files:
        if file:  # Skip empty lines
            print(f"   - {file}")
except subprocess.CalledProcessError:
    print("   - Unable to get staged files")

response = input("\n🔍 Continue with commit? (y/N): ")

if response.lower() in ['y', 'yes']:
    print("✅ Commit approved!")
    exit(0)
else:
    print("❌ Commit cancelled by user")
    exit(1)
```

### Task 5: Post-commit Celebration Hook
```python
#!/usr/bin/env python3
import subprocess
import random

# Get the commit hash and message
try:
    result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h - %s'], 
                           capture_output=True, text=True, check=True)
    commit_info = result.stdout.strip()
except subprocess.CalledProcessError:
    commit_info = "Unknown commit"

# Random celebration messages
celebrations = [
    "🎉 Awesome commit!",
    "🚀 Code deployed to Git!",
    "✨ Another masterpiece!",
    "🏆 Commit champion!",
    "💫 Git wizard in action!"
]

celebration = random.choice(celebrations)

print(f"\n{celebration}")
print(f"📝 {commit_info}")
print("🔄 Keep up the great work!\n")
```

## Advanced Examples

### Enhanced Interactive Hook with File Preview
```python
#!/usr/bin/env python3
import subprocess
import sys

def get_staged_files():
    """Get list of staged files"""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                               capture_output=True, text=True, check=True)
        return [f for f in result.stdout.strip().split('\n') if f]
    except subprocess.CalledProcessError:
        return []

def show_file_diff(filename):
    """Show diff for a specific file"""
    try:
        result = subprocess.run(['git', 'diff', '--cached', filename], 
                               capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return "Unable to show diff"

def main():
    print("🔍 Pre-commit Review Hook")
    print("=" * 40)
    
    staged_files = get_staged_files()
    
    if not staged_files:
        print("ℹ️  No staged files found")
        exit(0)
    
    print(f"📋 Found {len(staged_files)} staged file(s):")
    for i, file in enumerate(staged_files, 1):
        print(f"   {i}. {file}")
    
    print("\nOptions:")
    print("  c - Continue with commit")
    print("  s - Show diff for a file")
    print("  a - Abort commit")
    
    while True:
        choice = input("\nChoice (c/s/a): ").lower()
        
        if choice == 'c':
            print("✅ Proceeding with commit...")
            exit(0)
        elif choice == 'a':
            print("❌ Commit aborted")
            exit(1)
        elif choice == 's':
            try:
                file_num = int(input(f"File number (1-{len(staged_files)}): "))
                if 1 <= file_num <= len(staged_files):
                    filename = staged_files[file_num - 1]
                    print(f"\n--- Diff for {filename} ---")
                    diff = show_file_diff(filename)
                    print(diff)
                    print("--- End of diff ---\n")
                else:
                    print("Invalid file number")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Invalid choice. Use c, s, or a")

if __name__ == "__main__":
    main()
```

### Smart Conditional Hook (Multiple Conditions)
```python
#!/usr/bin/env python3
import datetime
import subprocess
import os

def get_current_branch():
    """Get the current Git branch"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                               capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"

def count_staged_files():
    """Count the number of staged files"""
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                               capture_output=True, text=True, check=True)
        files = [f for f in result.stdout.strip().split('\n') if f]
        return len(files)
    except subprocess.CalledProcessError:
        return 0

def main():
    print("🧠 Smart Pre-commit Hook")
    print("=" * 30)
    
    # Get current info
    now = datetime.datetime.now()
    branch = get_current_branch()
    staged_count = count_staged_files()
    hour = now.hour
    
    print(f"⏰ Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌿 Branch: {branch}")
    print(f"📁 Staged files: {staged_count}")
    
    # Condition 1: No commits to main/master without review
    if branch in ['main', 'master', 'production']:
        print("🚨 WARNING: Direct commits to protected branch!")
        response = input("Are you absolutely sure? (type 'YES' to confirm): ")
        if response != 'YES':
            print("❌ Commit blocked for safety")
            exit(1)
    
    # Condition 2: Discourage late-night commits
    if hour < 6 or hour > 22:
        print("🌙 Late night/early morning commit detected")
        print("💡 Consider reviewing in the morning")
        response = input("Continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Commit postponed")
            exit(1)
    
    # Condition 3: Large commits might need extra review
    if staged_count > 10:
        print(f"📦 Large commit detected ({staged_count} files)")
        print("💡 Consider breaking into smaller commits")
        response = input("Continue with large commit? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Large commit blocked")
            exit(1)
    
    # Condition 4: Friday afternoon check
    if now.weekday() == 4 and hour >= 15:  # Friday after 3 PM
        print("🍻 Friday afternoon deployment detected!")
        print("⚠️  Weekend deployments can be risky")
        response = input("Deploy on Friday afternoon? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Friday deployment avoided")
            exit(1)
    
    print("✅ All checks passed!")
    exit(0)

if __name__ == "__main__":
    main()
```

### Advanced Post-commit Statistics Hook
```python
#!/usr/bin/env python3
import subprocess
import datetime
import json
import os

def run_git_command(cmd):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_commit_stats():
    """Get statistics about the latest commit"""
    stats = {}
    
    # Basic commit info
    commit_hash = run_git_command(['git', 'rev-parse', 'HEAD'])
    commit_msg = run_git_command(['git', 'log', '-1', '--pretty=format:%s'])
    author = run_git_command(['git', 'log', '-1', '--pretty=format:%an'])
    
    # File changes
    files_changed = run_git_command(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'])
    if files_changed:
        files_list = files_changed.split('\n')
        stats['files_changed'] = len(files_list)
        stats['files_list'] = files_list
    else:
        stats['files_changed'] = 0
        stats['files_list'] = []
    
    # Line changes
    diff_stats = run_git_command(['git', 'diff', '--shortstat', 'HEAD~1', 'HEAD'])
    if diff_stats:
        # Parse something like "2 files changed, 10 insertions(+), 3 deletions(-)"
        parts = diff_stats.split(',')
        for part in parts:
            if 'insertion' in part:
                stats['insertions'] = int(part.strip().split()[0])
            elif 'deletion' in part:
                stats['deletions'] = int(part.strip().split()[0])
    
    if 'insertions' not in stats:
        stats['insertions'] = 0
    if 'deletions' not in stats:
        stats['deletions'] = 0
    
    # Repository stats
    total_commits = run_git_command(['git', 'rev-list', '--all', '--count'])
    current_branch = run_git_command(['git', 'branch', '--show-current'])
    
    stats.update({
        'commit_hash': commit_hash[:8] if commit_hash else 'unknown',
        'commit_message': commit_msg or 'No message',
        'author': author or 'Unknown',
        'total_commits': int(total_commits) if total_commits else 0,
        'current_branch': current_branch or 'unknown',
        'timestamp': datetime.datetime.now().isoformat()
    })
    
    return stats

def save_commit_log(stats):
    """Save commit statistics to a log file"""
    log_file = '.git/commit_stats.json'
    
    # Load existing data
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []
    else:
        data = []
    
    # Add new entry
    data.append(stats)
    
    # Keep only last 100 commits
    data = data[-100:]
    
    # Save back
    try:
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass  # Ignore save errors

def main():
    print("\n🎊 Commit Successful!")
    print("=" * 40)
    
    stats = get_commit_stats()
    
    print(f"📝 {stats['commit_hash']} - {stats['commit_message']}")
    print(f"👤 Author: {stats['author']}")
    print(f"🌿 Branch: {stats['current_branch']}")
    print(f"📊 Changes: {stats['files_changed']} files, +{stats['insertions']}/-{stats['deletions']} lines")
    print(f"🏆 Total commits: {stats['total_commits']}")
    
    # Fun facts
    if stats['files_changed'] > 5:
        print("📦 Big commit! Nice work on the comprehensive changes.")
    elif stats['insertions'] > 100:
        print("✍️  Lots of new code! Keep up the productivity.")
    elif stats['deletions'] > stats['insertions']:
        print("🧹 More deletions than additions - cleaning house!")
    else:
        print("👍 Clean commit!")
    
    # Save stats
    save_commit_log(stats)
    
    print("📈 Stats saved to .git/commit_stats.json")
    print("🚀 Keep coding!\n")

if __name__ == "__main__":
    main()
```

## Testing Scripts

### Hook Testing Framework
```python
#!/usr/bin/env python3
"""
Simple framework for testing Git hooks
"""
import subprocess
import tempfile
import os
import shutil

def create_test_repo():
    """Create a temporary Git repository for testing"""
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], check=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], check=True)
    return temp_dir

def install_hook(hook_name, hook_content):
    """Install a hook with given content"""
    hook_path = f'.git/hooks/{hook_name}'
    with open(hook_path, 'w') as f:
        f.write(hook_content)
    os.chmod(hook_path, 0o755)

def test_commit_with_files(files_content, commit_msg):
    """Create files and attempt a commit"""
    for filename, content in files_content.items():
        with open(filename, 'w') as f:
            f.write(content)
        subprocess.run(['git', 'add', filename], check=True)
    
    try:
        result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                               capture_output=True, text=True, check=True)
        return True, result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout + e.stderr

# Example usage
if __name__ == "__main__":
    # Create test environment
    test_dir = create_test_repo()
    print(f"Testing in: {test_dir}")
    
    # Install test hook
    hook_content = '''#!/usr/bin/env python3
import datetime
if datetime.datetime.now().weekday() == 4:  # Friday
    print("No Friday commits!")
    exit(1)
else:
    print("Commit allowed")
    exit(0)
'''
    
    install_hook('pre-commit', hook_content)
    
    # Test the hook
    success, output = test_commit_with_files(
        {'test.txt': 'Hello World'}, 
        'Test commit'
    )
    
    print(f"Commit successful: {success}")
    print(f"Output: {output}")
    
    # Cleanup
    os.chdir('/')
    shutil.rmtree(test_dir)
```