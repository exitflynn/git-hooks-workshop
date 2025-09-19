# Lab 1: Hello World & Exit Codes

## Learning Objectives
- Write your first custom Git hook from scratch
- Understand how exit codes control Git operations
- Create both informational and blocking hooks
- Learn Python basics for Git hooks

## Overview

In this lab, you'll create your first custom Git hooks using Python. You'll learn how exit codes determine whether Git operations proceed or are blocked, and you'll build both informational hooks (that don't block) and validation hooks (that can block operations).

## Setup

1. Create a new directory for this lab:
   ```bash
   mkdir lab1-practice
   cd lab1-practice
   git init
   ```

2. Ensure you have Python 3 available:
   ```bash
   python3 --version
   ```

## Tasks

### Task 1: Hello World Pre-commit Hook

Create your first custom pre-commit hook that simply prints a greeting.

1. Create the hook file:
   ```bash
   touch .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. Edit `.git/hooks/pre-commit` and add:
   ```python
   #!/usr/bin/env python3
   
   print("🚀 Hello from your custom pre-commit hook!")
   print("📝 Running pre-commit checks...")
   
   # Exit with 0 to allow the commit to proceed
   exit(0)
   ```

3. Test the hook:
   ```bash
   echo "Test content" > test.txt
   git add test.txt
   git commit -m "Testing hello world hook"
   ```

**Expected Result**: You should see your greeting message, and the commit should succeed.

### Task 2: Understanding Exit Codes

Now let's create a hook that blocks commits to understand exit codes.

1. Modify your pre-commit hook:
   ```python
   #!/usr/bin/env python3
   
   print("🚀 Hello from your custom pre-commit hook!")
   print("❌ This hook will block your commit!")
   
   # Exit with 1 to block the commit
   exit(1)
   ```

2. Test the blocking behavior:
   ```bash
   echo "More content" >> test.txt
   git add test.txt
   git commit -m "This should be blocked"
   ```

**Expected Result**: The commit should be blocked with an error message.

### Task 3: Conditional Hook Logic

Create a hook that only blocks commits on Friday (just for fun!).

1. Update your pre-commit hook:
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

2. Test the conditional logic:
   ```bash
   git add .
   git commit -m "Testing conditional hook"
   ```

### Task 4: Interactive Hook

Create a hook that asks for user confirmation.

1. Create a new pre-commit hook:
   ```python
   #!/usr/bin/env python3
   import sys
   
   print("🤔 Are you sure you want to commit these changes?")
   print("📋 Staged files:")
   
   # Show staged files (we'll learn about git commands in hooks later)
   import subprocess
   result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                          capture_output=True, text=True)
   
   if result.returncode == 0:
       staged_files = result.stdout.strip().split('\n')
       for file in staged_files:
           if file:  # Skip empty lines
               print(f"   - {file}")
   
   response = input("\n🔍 Continue with commit? (y/N): ")
   
   if response.lower() in ['y', 'yes']:
       print("✅ Commit approved!")
       exit(0)
   else:
       print("❌ Commit cancelled by user")
       exit(1)
   ```

2. Test the interactive hook:
   ```bash
   echo "Interactive test" > interactive.txt
   git add interactive.txt
   git commit -m "Testing interactive hook"
   ```

### Task 5: Post-commit Celebration Hook

Create a post-commit hook that celebrates successful commits.

1. Create a post-commit hook:
   ```bash
   touch .git/hooks/post-commit
   chmod +x .git/hooks/post-commit
   ```

2. Add celebration content:
   ```python
   #!/usr/bin/env python3
   import subprocess
   import random
   
   # Get the commit hash and message
   result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h - %s'], 
                          capture_output=True, text=True)
   
   if result.returncode == 0:
       commit_info = result.stdout.strip()
   else:
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

3. Test the post-commit hook:
   ```bash
   echo "Celebration test" > celebration.txt
   git add celebration.txt
   git commit -m "Testing post-commit celebration"
   ```

## Key Concepts

### Exit Codes in Git Hooks

| Exit Code | Meaning | Git Behavior |
|-----------|---------|--------------|
| 0 | Success | Operation continues |
| 1-255 | Error/Failure | Operation is blocked |

### Hook Types and Exit Code Effects

1. **Pre-commit**: Exit code 1 prevents the commit
2. **Post-commit**: Exit codes are ignored (commit already happened)
3. **Pre-push**: Exit code 1 prevents the push
4. **Commit-msg**: Exit code 1 prevents the commit

### Python in Git Hooks

- Always use shebang: `#!/usr/bin/env python3`
- Make files executable: `chmod +x`
- Use `subprocess` to run git commands
- Handle errors gracefully

### Bypassing Hooks

Users can bypass client-side hooks with:
```bash
git commit --no-verify -m "Bypass hooks"
git push --no-verify
```

## Troubleshooting

### Python Not Found?
Make sure Python 3 is installed and the shebang is correct:
```bash
which python3
```

### Permission Denied?
Make sure the hook is executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Import Errors?
Git hooks run in a minimal environment. Stick to standard library modules or ensure dependencies are available.

### Interactive Input Not Working?
Some Git interfaces might not handle interactive input well. Test in a terminal.

## Best Practices

1. **Always provide clear feedback** to users
2. **Use meaningful exit codes** (0 for success, 1 for failure)
3. **Include bypass instructions** for emergency situations
4. **Keep hooks fast** - users will disable slow hooks
5. **Handle errors gracefully** - don't crash on unexpected input

## Next Steps

In Lab 2, you'll build a more sophisticated linter hook that checks code quality and enforces coding standards.

## Summary

You've learned:
- How to write custom Git hooks in Python
- The importance of exit codes in controlling Git operations
- How to create both informational and blocking hooks
- How to make hooks interactive and conditional
- The difference between pre-commit and post-commit hooks

Great job! You're now ready to build more complex hooks that enforce real development policies.