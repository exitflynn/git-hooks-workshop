# Lab 0 Solutions

## Task Answers

### Task 1: What does the default pre-commit hook check for?
The default pre-commit hook checks for:
- Trailing whitespace at the end of lines
- Files that end with incomplete lines (missing newline at end of file)

## Complete Solution Scripts

### Enhanced Pre-commit Hook
Here's an enhanced version of the pre-commit hook that provides better feedback:

```bash
#!/bin/sh
# Enhanced pre-commit hook with better error messages

echo "Running pre-commit checks..."

# Check for trailing whitespace
if git rev-parse --verify HEAD >/dev/null 2>&1
then
    against=HEAD
else
    # Initial commit: diff against an empty tree object
    against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Find files with trailing whitespace
bad_files=$(git diff-index --check --cached $against)

if [ "$bad_files" ]; then
    echo "Error: Found trailing whitespace in the following files:"
    echo "$bad_files"
    echo ""
    echo "Please remove trailing whitespace and try again."
    echo "You can fix this automatically with:"
    echo "  git diff --cached --name-only | xargs sed -i 's/[[:space:]]*$//'"
    exit 1
fi

echo "Pre-commit checks passed!"
exit 0
```

### Custom Post-commit Hook
Here's a custom post-commit hook that provides useful information:

```bash
#!/bin/sh
# Custom post-commit hook

echo "📝 Commit successful!"
echo "📊 Repository stats:"
echo "   - Total commits: $(git rev-list --all --count)"
echo "   - Current branch: $(git branch --show-current)"
echo "   - Last commit: $(git log -1 --pretty=format:'%h - %s (%cr)')"
echo ""
```

## Testing Scripts

### Create Test Repository
```bash
#!/bin/bash
# Script to create a test repository with various scenarios

mkdir -p test-repo
cd test-repo
git init

# Test 1: File with trailing whitespace
echo "Line with trailing spaces   " > bad-file.txt
echo "Clean line" > good-file.txt

# Set up the enhanced pre-commit hook
cp ../solutions/enhanced-pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "Test repository created!"
echo "Try: git add . && git commit -m 'Test commit'"
```

### Whitespace Fixer Script
```bash
#!/bin/bash
# Script to automatically fix trailing whitespace

echo "Fixing trailing whitespace in staged files..."

# Get list of staged files
staged_files=$(git diff --cached --name-only)

if [ -z "$staged_files" ]; then
    echo "No staged files found."
    exit 0
fi

# Fix trailing whitespace in each staged file
for file in $staged_files; do
    if [ -f "$file" ]; then
        echo "Fixing: $file"
        sed -i 's/[[:space:]]*$//' "$file"
        git add "$file"  # Re-stage the fixed file
    fi
done

echo "Trailing whitespace fixed in staged files!"
```

## Verification Commands

```bash
# Check if hooks are executable
ls -la .git/hooks/ | grep -v sample

# Test hook execution manually
.git/hooks/pre-commit

# View hook content
cat .git/hooks/pre-commit

# Check git configuration related to hooks
git config --list | grep hook
```

## Common Issues and Solutions

### Issue 1: Hook not executable
```bash
# Solution:
chmod +x .git/hooks/pre-commit
```

### Issue 2: Wrong line endings (Windows)
```bash
# Solution: Convert to Unix line endings
dos2unix .git/hooks/pre-commit
```

### Issue 3: Python/Ruby script issues
```bash
# Ensure proper shebang line:
#!/usr/bin/env python3
# or
#!/usr/bin/env ruby
```

## Advanced Examples

### Multi-language Pre-commit Hook
```bash
#!/bin/sh
# Multi-language pre-commit hook

echo "Running comprehensive pre-commit checks..."

# Check for trailing whitespace
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    against=HEAD
else
    against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Check trailing whitespace
if git diff-index --check --cached $against; then
    echo "✅ No trailing whitespace found"
else
    echo "❌ Trailing whitespace detected!"
    exit 1
fi

# Check for Python files and run basic syntax check
python_files=$(git diff --cached --name-only --diff-filter=AM | grep '\.py$')
if [ "$python_files" ]; then
    echo "Checking Python syntax..."
    for file in $python_files; do
        python3 -m py_compile "$file"
        if [ $? -ne 0 ]; then
            echo "❌ Python syntax error in $file"
            exit 1
        fi
    done
    echo "✅ Python syntax checks passed"
fi

# Check for large files (>1MB)
large_files=$(git diff --cached --name-only | xargs -I {} sh -c 'if [ -f "{}" ] && [ $(stat -f%z "{}" 2>/dev/null || stat -c%s "{}" 2>/dev/null || echo 0) -gt 1048576 ]; then echo "{}"; fi')
if [ "$large_files" ]; then
    echo "❌ Large files detected (>1MB):"
    echo "$large_files"
    echo "Consider using Git LFS for large files"
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0
```