# Lab 0: Basic Hooks Setup

## Learning Objectives
- Understand where Git hooks are stored
- Learn about the default sample hooks
- Activate your first Git hook
- Understand how hooks are executed

## Overview

Git hooks are stored in the `.git/hooks` directory of your repository. When you initialize a new repository with `git init`, Git populates this directory with example scripts that end with `.sample`. To activate a hook, you simply remove the `.sample` extension and make the file executable.

## Setup

1. Create a new Git repository for this lab:
   ```bash
   mkdir lab0-practice
   cd lab0-practice
   git init
   ```

2. Explore the hooks directory:
   ```bash
   ls -la .git/hooks/
   ```

You should see several `.sample` files like:
- `pre-commit.sample`
- `pre-push.sample`
- `post-commit.sample`
- `commit-msg.sample`

## Tasks

### Task 1: Examine Default Hooks

1. Look at the content of the pre-commit sample:
   ```bash
   cat .git/hooks/pre-commit.sample
   ```

2. Read through the comments to understand what this hook does.

**Question**: What does the default pre-commit hook check for?

### Task 2: Activate the Pre-commit Hook

1. Copy the sample to create an active hook:
   ```bash
   cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
   ```

2. Make it executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

### Task 3: Test the Hook

1. Create a file with trailing whitespace:
   ```bash
   echo "Hello World   " > test.txt
   ```

2. Add the file to staging:
   ```bash
   git add test.txt
   ```

3. Try to commit:
   ```bash
   git commit -m "Test commit with trailing whitespace"
   ```

**Expected Result**: The commit should be blocked due to trailing whitespace.

### Task 4: Fix and Commit

1. Remove the trailing whitespace:
   ```bash
   echo "Hello World" > test.txt
   ```

2. Add and commit again:
   ```bash
   git add test.txt
   git commit -m "Test commit without trailing whitespace"
   ```

**Expected Result**: The commit should succeed.

### Task 5: Explore Other Hooks

1. Activate the post-commit hook:
   ```bash
   cp .git/hooks/post-commit.sample .git/hooks/post-commit
   chmod +x .git/hooks/post-commit
   ```

2. Make another commit to see the post-commit hook in action:
   ```bash
   echo "Another line" >> test.txt
   git add test.txt
   git commit -m "Testing post-commit hook"
   ```

## Key Concepts

### Hook Types

1. **Pre-commit**: Runs before a commit is created
   - Can block commits by exiting with non-zero status
   - Used for code quality checks

2. **Post-commit**: Runs after a commit is successfully created
   - Cannot block the commit
   - Used for notifications or cleanup

3. **Pre-push**: Runs before pushing to a remote
   - Can block pushes
   - Used for final validation

4. **Commit-msg**: Runs during commit creation
   - Can modify or validate commit messages
   - Receives commit message as parameter

### Exit Codes

- **Exit 0**: Success, allow the Git operation to continue
- **Exit 1** (or any non-zero): Failure, block the Git operation

### Making Hooks Executable

Hooks must be executable to run:
```bash
chmod +x .git/hooks/hook-name
```

## Troubleshooting

### Hook Not Running?
1. Check if the file is executable: `ls -la .git/hooks/`
2. Ensure there's no `.sample` extension
3. Check for syntax errors in the script

### Permission Denied?
```bash
chmod +x .git/hooks/your-hook-name
```

### Want to Bypass a Hook?
Use the `--no-verify` flag:
```bash
git commit --no-verify -m "Bypass hooks"
```

## Next Steps

Now that you understand the basics of Git hooks, proceed to Lab 1 where you'll create your own custom hooks and learn about exit codes in detail.

## Summary

You've learned:
- Where Git hooks are stored (`.git/hooks/`)
- How to activate sample hooks by removing `.sample` extension
- The difference between pre-commit and post-commit hooks
- How exit codes control Git operations
- How to make hooks executable

In the next lab, you'll write your first custom hook from scratch!