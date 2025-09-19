# Lab 3 Solutions

## Complete Solution Scripts

### Task 1: Basic Jira Validation
```python
#!/usr/bin/env python3
import sys
import re

def validate_jira_reference(message):
    """Check if commit message contains a Jira ticket reference"""
    # Pattern for Jira tickets: PROJECT-123 format
    jira_pattern = r'[A-Z]{2,}-\d+'
    
    if re.search(jira_pattern, message):
        return True, None
    else:
        return False, "Commit message must contain a Jira ticket reference (e.g., PROJ-123)"

def main():
    if len(sys.argv) != 2:
        print("Usage: commit-msg <commit-message-file>")
        sys.exit(1)
    
    message_file = sys.argv[1]
    
    try:
        with open(message_file, 'r') as f:
            commit_message = f.read().strip()
    except IOError as e:
        print(f"Error reading commit message file: {e}")
        sys.exit(1)
    
    print("🎫 Validating Jira ticket reference...")
    
    is_valid, error_msg = validate_jira_reference(commit_message)
    
    if is_valid:
        print("✅ Jira ticket reference found")
        sys.exit(0)
    else:
        print(f"❌ {error_msg}")
        print(f"📝 Your message: '{commit_message}'")
        print("💡 Example: 'PROJ-123: Add user authentication'")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Task 2: Enhanced Jira Validation
```python
#!/usr/bin/env python3
import sys
import re

class JiraValidator:
    def __init__(self):
        # Different Jira patterns to support
        self.patterns = [
            r'[A-Z]{2,}-\d+',  # Standard: PROJ-123
            r'[A-Z]{2,}_\d+',  # Underscore: PROJ_123
            r'[A-Z]{2,}\s*#\d+',  # Hash: PROJ #123
        ]
        
        # Allowed positions for Jira tickets
        self.position_patterns = [
            r'^[A-Z]{2,}[_-]?\d+:',  # Start: "PROJ-123: message"
            r'\[[A-Z]{2,}[_-]?\d+\]',  # Brackets: "[PROJ-123] message"
            r'[A-Z]{2,}[_-]?\d+',  # Anywhere in message
        ]
    
    def validate(self, message):
        """Validate Jira ticket reference in commit message"""
        # Check each position pattern
        for pattern in self.position_patterns:
            if re.search(pattern, message):
                return True, None
        
        # If no position pattern matches, check for any Jira pattern
        for pattern in self.patterns:
            if re.search(pattern, message):
                return False, ("Jira ticket found but in wrong format. "
                             "Use format: 'PROJ-123: message' or '[PROJ-123] message'")
        
        return False, "No Jira ticket reference found"
    
    def extract_tickets(self, message):
        """Extract all Jira tickets from message"""
        tickets = []
        for pattern in self.patterns:
            matches = re.findall(pattern, message)
            tickets.extend(matches)
        return tickets

def validate_message_structure(message):
    """Validate basic message structure"""
    lines = message.split('\n')
    
    if not lines[0].strip():
        return False, "Commit message cannot be empty"
    
    if len(lines[0]) > 72:
        return False, f"Subject line too long ({len(lines[0])} chars). Keep under 72 characters"
    
    # Check for proper separation between subject and body
    if len(lines) > 1 and lines[1].strip():
        return False, "Separate subject from body with a blank line"
    
    return True, None

def main():
    if len(sys.argv) != 2:
        print("Usage: commit-msg <commit-message-file>")
        sys.exit(1)
    
    message_file = sys.argv[1]
    
    try:
        with open(message_file, 'r') as f:
            commit_message = f.read().strip()
    except IOError as e:
        print(f"Error reading commit message file: {e}")
        sys.exit(1)
    
    print("📝 Validating commit message...")
    print(f"Message: '{commit_message}'")
    
    # Validate message structure
    is_valid, error_msg = validate_message_structure(commit_message)
    if not is_valid:
        print(f"❌ Structure error: {error_msg}")
        sys.exit(1)
    
    # Validate Jira reference
    validator = JiraValidator()
    is_valid, error_msg = validator.validate(commit_message)
    
    if is_valid:
        tickets = validator.extract_tickets(commit_message)
        print(f"✅ Valid commit message with ticket(s): {', '.join(tickets)}")
        sys.exit(0)
    else:
        print(f"❌ {error_msg}")
        print("\n💡 Valid formats:")
        print("   • PROJ-123: Your commit message")
        print("   • [PROJ-123] Your commit message")
        print("   • Fix issue PROJ-123 in user auth")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Task 3: Complete Conventional Commits with Jira
```python
#!/usr/bin/env python3
import sys
import re
import json
import os

class ConventionalCommitValidator:
    def __init__(self):
        # Conventional commit types
        self.valid_types = [
            'feat', 'fix', 'docs', 'style', 'refactor',
            'perf', 'test', 'chore', 'build', 'ci'
        ]
        
        # Conventional commit pattern
        # type(scope)!: description
        self.pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|build|ci)(\([^)]+\))?(!)?:\s+(.+)$'
        
    def validate(self, message):
        """Validate conventional commit format"""
        lines = message.split('\n')
        subject = lines[0]
        
        match = re.match(self.pattern, subject)
        if not match:
            return False, self._format_error_message(subject)
        
        commit_type, scope, breaking, description = match.groups()
        
        # Validate description
        if len(description) < 3:
            return False, "Description too short (minimum 3 characters)"
        
        if description[0].isupper():
            return False, "Description should start with lowercase letter"
        
        if description.endswith('.'):
            return False, "Description should not end with a period"
        
        return True, {
            'type': commit_type,
            'scope': scope[1:-1] if scope else None,  # Remove parentheses
            'breaking': breaking is not None,
            'description': description
        }
    
    def _format_error_message(self, subject):
        return (
            f"Invalid conventional commit format: '{subject}'\n"
            "Expected format: type(scope): description\n"
            f"Valid types: {', '.join(self.valid_types)}"
        )

class JiraValidator:
    def __init__(self):
        self.pattern = r'[A-Z]{2,}-\d+'
    
    def validate(self, message):
        """Check if message contains Jira ticket"""
        if re.search(self.pattern, message):
            return True, re.findall(self.pattern, message)
        return False, None

class CommitMessageConfig:
    def __init__(self, config_file='.commit-config.json'):
        self.require_jira = True
        self.require_conventional = False
        self.jira_in_description = True
        self.max_subject_length = 72
        self.allow_merge_commits = True
        
        if os.path.exists(config_file):
            self._load_config(config_file)
    
    def _load_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.require_jira = config.get('require_jira', self.require_jira)
            self.require_conventional = config.get('require_conventional', self.require_conventional)
            self.jira_in_description = config.get('jira_in_description', self.jira_in_description)
            self.max_subject_length = config.get('max_subject_length', self.max_subject_length)
            self.allow_merge_commits = config.get('allow_merge_commits', self.allow_merge_commits)
        except (json.JSONDecodeError, IOError):
            pass  # Use defaults if config file is invalid

def is_merge_commit(message):
    """Check if this is a merge commit"""
    return message.startswith('Merge ') or 'Merge pull request' in message

def validate_commit_message(message, config):
    """Main validation function"""
    lines = message.split('\n')
    subject = lines[0].strip()
    
    if not subject:
        return False, "Commit message cannot be empty"
    
    # Allow merge commits if configured
    if is_merge_commit(message) and config.allow_merge_commits:
        return True, "Merge commit allowed"
    
    # Check subject length
    if len(subject) > config.max_subject_length:
        return False, f"Subject line too long ({len(subject)} > {config.max_subject_length})"
    
    results = {'conventional': None, 'jira': None}
    
    # Validate conventional commit format if required
    if config.require_conventional:
        conv_validator = ConventionalCommitValidator()
        is_valid, result = conv_validator.validate(message)
        
        if not is_valid:
            return False, f"Conventional commit error: {result}"
        
        results['conventional'] = result
    
    # Validate Jira ticket if required
    if config.require_jira:
        jira_validator = JiraValidator()
        has_jira, tickets = jira_validator.validate(message)
        
        if not has_jira:
            return False, "Jira ticket reference required"
        
        results['jira'] = tickets
    
    return True, results

def main():
    if len(sys.argv) != 2:
        print("Usage: commit-msg <commit-message-file>")
        sys.exit(1)
    
    message_file = sys.argv[1]
    
    try:
        with open(message_file, 'r') as f:
            commit_message = f.read().strip()
    except IOError as e:
        print(f"Error reading commit message file: {e}")
        sys.exit(1)
    
    # Load configuration
    config = CommitMessageConfig()
    
    print("📝 Advanced Commit Message Validation")
    print("=" * 40)
    print(f"Config: conventional={config.require_conventional}, jira={config.require_jira}")
    
    # Validate the message
    is_valid, result = validate_commit_message(commit_message, config)
    
    if is_valid:
        print("✅ Commit message validation passed!")
        
        if isinstance(result, dict):
            if result.get('conventional'):
                conv = result['conventional']
                print(f"   Type: {conv['type']}")
                if conv['scope']:
                    print(f"   Scope: {conv['scope']}")
                if conv['breaking']:
                    print("   ⚠️  Breaking change!")
            
            if result.get('jira'):
                print(f"   Jira tickets: {', '.join(result['jira'])}")
        
        sys.exit(0)
    else:
        print(f"❌ Validation failed: {result}")
        
        if config.require_conventional:
            print("\n💡 Conventional commit format:")
            print("   feat(scope): add new feature")
            print("   fix: resolve bug issue")
            print("   docs: update documentation")
        
        if config.require_jira:
            print("\n💡 Include Jira ticket:")
            print("   feat(auth): add login PROJ-123")
            print("   fix: resolve PROJ-456 database issue")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Task 4: Interactive Commit Helper
```python
#!/usr/bin/env python3
"""
Interactive commit message helper
Usage: python3 commit_helper.py
"""
import sys
import re
import subprocess
import os

class CommitHelper:
    def __init__(self):
        self.types = {
            'feat': 'A new feature',
            'fix': 'A bug fix',
            'docs': 'Documentation only changes',
            'style': 'Changes that do not affect the meaning of the code',
            'refactor': 'A code change that neither fixes a bug nor adds a feature',
            'perf': 'A code change that improves performance',
            'test': 'Adding missing tests or correcting existing tests',
            'chore': 'Changes to the build process or auxiliary tools',
            'build': 'Changes that affect the build system or external dependencies',
            'ci': 'Changes to our CI configuration files and scripts'
        }
    
    def get_type(self):
        """Get commit type from user"""
        print("📋 Select commit type:")
        for i, (type_name, description) in enumerate(self.types.items(), 1):
            print(f"   {i:2}. {type_name:10} - {description}")
        
        while True:
            try:
                choice = input("\nEnter number (1-10): ")
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(self.types):
                    return list(self.types.keys())[choice_idx]
                else:
                    print("Invalid choice. Please enter 1-10.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_scope(self):
        """Get optional scope"""
        scope = input("🎯 Enter scope (optional, e.g., 'auth', 'api', 'ui'): ").strip()
        return scope if scope else None
    
    def get_description(self):
        """Get commit description"""
        while True:
            description = input("📝 Enter description (start with lowercase, no period): ").strip()
            
            if len(description) < 3:
                print("Description too short (minimum 3 characters)")
                continue
            
            if description[0].isupper():
                print("Description should start with lowercase letter")
                continue
            
            if description.endswith('.'):
                print("Description should not end with a period")
                continue
            
            return description
    
    def get_jira_ticket(self):
        """Get Jira ticket reference"""
        while True:
            ticket = input("🎫 Enter Jira ticket (e.g., PROJ-123): ").strip().upper()
            
            if not ticket:
                return None
            
            if re.match(r'^[A-Z]{2,}-\d+$', ticket):
                return ticket
            else:
                print("Invalid Jira format. Use format: PROJ-123")
    
    def get_breaking_change(self):
        """Check if this is a breaking change"""
        response = input("💥 Is this a breaking change? (y/N): ").strip().lower()
        return response in ['y', 'yes']
    
    def get_body(self):
        """Get optional commit body"""
        print("📄 Enter commit body (optional, press Enter twice to finish):")
        lines = []
        empty_lines = 0
        
        while True:
            line = input()
            if not line:
                empty_lines += 1
                if empty_lines >= 2:
                    break
            else:
                empty_lines = 0
                lines.append(line)
        
        return '\n'.join(lines) if lines else None
    
    def preview_staged_files(self):
        """Show staged files to user"""
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--name-status'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout:
                print("📁 Staged files:")
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status, filename = line.split('\t', 1)
                        status_icon = {'A': '➕', 'M': '📝', 'D': '🗑️'}.get(status, '❓')
                        print(f"   {status_icon} {filename}")
            else:
                print("📁 No staged files found")
        except subprocess.CalledProcessError:
            print("📁 Unable to get staged files")
    
    def build_message(self):
        """Build complete commit message interactively"""
        print("🚀 Interactive Commit Message Builder")
        print("=" * 40)
        
        # Show staged files first
        self.preview_staged_files()
        print()
        
        # Get all components
        commit_type = self.get_type()
        scope = self.get_scope()
        breaking = self.get_breaking_change()
        description = self.get_description()
        jira_ticket = self.get_jira_ticket()
        
        # Build subject line
        subject = commit_type
        if scope:
            subject += f"({scope})"
        if breaking:
            subject += "!"
        subject += f": {description}"
        
        # Add Jira ticket to description if provided
        if jira_ticket:
            subject += f" {jira_ticket}"
        
        # Get optional body
        body = self.get_body()
        
        # Build complete message
        message = subject
        if body:
            message += f"\n\n{body}"
        
        print("\n📋 Generated commit message:")
        print("-" * 40)
        print(message)
        print("-" * 40)
        
        return message
    
    def validate_message(self, message):
        """Validate the generated message"""
        # Basic validation
        lines = message.split('\n')
        subject = lines[0]
        
        if len(subject) > 72:
            print(f"⚠️  Warning: Subject line is {len(subject)} characters (recommended: ≤72)")
        
        # Check for Jira ticket
        if not re.search(r'[A-Z]{2,}-\d+', message):
            print("⚠️  Warning: No Jira ticket found in message")
        
        return True
    
    def commit_with_message(self, message):
        """Perform the actual commit"""
        try:
            result = subprocess.run(['git', 'commit', '-m', message], 
                                  capture_output=True, text=True, check=True)
            print("✅ Commit successful!")
            print(f"📝 {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Commit failed: {e.stderr}")
            return False

def main():
    helper = CommitHelper()
    
    # Check if we're in a git repository
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        sys.exit(1)
    
    # Check if there are staged changes
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'])
        if result.returncode != 0:
            # There are staged changes
            message = helper.build_message()
            
            # Validate the message
            helper.validate_message(message)
            
            confirm = input("\n🤔 Proceed with commit? (Y/n): ").strip().lower()
            if confirm in ['', 'y', 'yes']:
                helper.commit_with_message(message)
            else:
                print("Commit cancelled")
                print(f"💾 Generated message saved for reference:\n{message}")
        else:
            print("❌ No staged changes found. Use 'git add' first.")
    except subprocess.CalledProcessError:
        print("❌ Error checking git status")

if __name__ == "__main__":
    main()
```

## Configuration Examples

### Basic Configuration (.commit-config.json)
```json
{
  "require_jira": true,
  "require_conventional": false,
  "jira_in_description": true,
  "max_subject_length": 72,
  "allow_merge_commits": true
}
```

### Strict Configuration
```json
{
  "require_jira": true,
  "require_conventional": true,
  "jira_in_description": true,
  "max_subject_length": 50,
  "allow_merge_commits": false,
  "valid_jira_projects": ["PROJ", "FEAT", "BUG"],
  "required_conventional_types": ["feat", "fix", "docs", "chore"]
}
```

### Team-Specific Configuration
```json
{
  "require_jira": true,
  "require_conventional": true,
  "jira_in_description": false,
  "max_subject_length": 72,
  "allow_merge_commits": true,
  "jira_patterns": [
    "[A-Z]{2,}-\\d+",
    "BUG-\\d+",
    "STORY-\\d+"
  ],
  "custom_types": {
    "hotfix": "Emergency production fix",
    "release": "Release preparation"
  }
}
```

## Testing Utilities

### Message Validator Test
```python
#!/usr/bin/env python3
"""
Test utility for commit message validation
"""
import sys
import tempfile
import os

def test_message(message, validator_script):
    """Test a commit message with the validator"""
    # Create temporary file with the message
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.msg') as f:
        f.write(message)
        temp_file = f.name
    
    try:
        # Run the validator
        import subprocess
        result = subprocess.run([sys.executable, validator_script, temp_file], 
                               capture_output=True, text=True)
        
        return result.returncode == 0, result.stdout, result.stderr
    finally:
        # Clean up
        os.unlink(temp_file)

def run_tests():
    """Run test suite for commit message validation"""
    validator = '.git/hooks/commit-msg'
    
    test_cases = [
        # Valid messages
        ("PROJ-123: add user authentication", True),
        ("[PROJ-456] fix login bug", True),
        ("feat(auth): add PROJ-789 oauth support", True),
        
        # Invalid messages
        ("add user authentication", False),  # No Jira
        ("proj-123: lowercase project", False),  # Lowercase
        ("PROJ-123", False),  # No description
        ("", False),  # Empty message
    ]
    
    print("🧪 Running commit message tests...")
    passed = 0
    
    for message, should_pass in test_cases:
        success, stdout, stderr = test_message(message, validator)
        
        if success == should_pass:
            print(f"✅ PASS: '{message}'")
            passed += 1
        else:
            print(f"❌ FAIL: '{message}'")
            print(f"   Expected: {'PASS' if should_pass else 'FAIL'}")
            print(f"   Got: {'PASS' if success else 'FAIL'}")
            if stderr:
                print(f"   Error: {stderr}")
    
    print(f"\n📊 Results: {passed}/{len(test_cases)} tests passed")

if __name__ == "__main__":
    run_tests()
```

### Batch Message Generator
```python
#!/usr/bin/env python3
"""
Generate sample commit messages for testing
"""
import random

class MessageGenerator:
    def __init__(self):
        self.types = ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
        self.scopes = ['auth', 'api', 'ui', 'db', 'config', 'tests']
        self.projects = ['PROJ', 'FEAT', 'BUG', 'TASK']
        self.actions = [
            'add', 'remove', 'update', 'fix', 'improve', 'refactor',
            'implement', 'create', 'delete', 'optimize'
        ]
        self.objects = [
            'user authentication', 'database connection', 'error handling',
            'logging system', 'configuration file', 'test suite',
            'API endpoint', 'user interface', 'validation logic'
        ]
    
    def generate_conventional_jira(self):
        """Generate conventional commit with Jira ticket"""
        commit_type = random.choice(self.types)
        scope = random.choice(self.scopes)
        action = random.choice(self.actions)
        obj = random.choice(self.objects)
        project = random.choice(self.projects)
        ticket_num = random.randint(100, 999)
        
        return f"{commit_type}({scope}): {action} {obj} {project}-{ticket_num}"
    
    def generate_simple_jira(self):
        """Generate simple message with Jira ticket"""
        action = random.choice(self.actions).capitalize()
        obj = random.choice(self.objects)
        project = random.choice(self.projects)
        ticket_num = random.randint(100, 999)
        
        return f"{project}-{ticket_num}: {action} {obj}"
    
    def generate_invalid(self):
        """Generate invalid commit messages"""
        invalid_types = [
            "add user authentication",  # No Jira
            "proj-123: lowercase project",  # Lowercase Jira
            "PROJ-123",  # No description
            "Very long commit message that exceeds the recommended character limit and should be rejected by validation",  # Too long
            "Fix bugs.",  # Period at end
        ]
        return random.choice(invalid_types)
    
    def generate_batch(self, count=10):
        """Generate a batch of mixed messages"""
        messages = []
        
        for _ in range(count // 3):
            messages.append(('valid_conv', self.generate_conventional_jira()))
            messages.append(('valid_simple', self.generate_simple_jira()))
            messages.append(('invalid', self.generate_invalid()))
        
        return messages

def main():
    generator = MessageGenerator()
    
    print("🎲 Sample Commit Messages")
    print("=" * 30)
    
    messages = generator.generate_batch(15)
    
    for category, message in messages:
        icon = {'valid_conv': '✅', 'valid_simple': '✅', 'invalid': '❌'}[category]
        print(f"{icon} {category:12} | {message}")

if __name__ == "__main__":
    main()
```