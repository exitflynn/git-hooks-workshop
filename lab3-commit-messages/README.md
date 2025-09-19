# Lab 3: Commit Message Validation

## Learning Objectives
- Implement commit message validation using the `commit-msg` hook
- Enforce Jira ticket references in commit messages
- Understand conventional commit format validation
- Learn regex patterns for message parsing
- Build configurable message validation rules

## Overview

In this lab, you'll create a `commit-msg` hook that enforces commit message standards. This is crucial for maintaining a clean, traceable Git history and ensuring proper integration with project management tools like Jira. You'll start with basic Jira ticket validation and extend to full conventional commit format support.

## Setup

1. Create a new directory for this lab:
   ```bash
   mkdir lab3-practice
   cd lab3-practice
   git init
   git config user.email "test@example.com"
   git config user.name "Test User"
   ```

2. Understand the commit-msg hook:
   - Receives the commit message file path as first argument
   - Can modify the message file
   - Exit code 1 blocks the commit

## Tasks

### Task 1: Basic Jira Ticket Validation

Create a commit-msg hook that ensures all commits reference a Jira ticket.

1. Create the hook file:
   ```bash
   touch .git/hooks/commit-msg
   chmod +x .git/hooks/commit-msg
   ```

2. Implement basic Jira validation:
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

3. Test the Jira validation:
   ```bash
   # This should fail
   echo "Test file" > test.txt
   git add test.txt
   git commit -m "Add test file"
   
   # This should succeed
   git commit -m "PROJ-123: Add test file"
   ```

### Task 2: Enhanced Jira Validation with Multiple Formats

Extend the validator to handle different Jira ticket formats and positions.

1. Update the commit-msg hook:
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

2. Test different Jira formats:
   ```bash
   # Test various valid formats
   git commit --amend -m "PROJ-123: Fix user authentication bug"
   git commit --amend -m "[PROJ-456] Add new feature"
   git commit --amend -m "Fix critical issue PROJ-789"
   
   # Test invalid formats
   git commit --amend -m "Fix user authentication"  # Should fail
   git commit --amend -m "proj-123: lowercase project"  # Should fail
   ```

### Task 3: Conventional Commits Support (Stretch Goal)

Implement validation for conventional commit format with Jira integration.

1. Create an advanced commit-msg hook:
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

2. Create a configuration file:
   ```bash
   cat > .commit-config.json << 'EOF'
   {
     "require_jira": true,
     "require_conventional": true,
     "jira_in_description": true,
     "max_subject_length": 72,
     "allow_merge_commits": true
   }
   EOF
   ```

3. Test conventional commits with Jira:
   ```bash
   # Valid conventional + Jira
   git add .commit-config.json
   git commit -m "feat(validation): add PROJ-123 commit message validation"
   
   # Test breaking change
   echo "# New feature" > feature.txt
   git add feature.txt
   git commit -m "feat!: add PROJ-456 breaking API change"
   
   # Test invalid format
   git commit -m "Added new feature PROJ-789"  # Should fail - not conventional
   ```

### Task 4: Interactive Message Editor

Create a helper that guides users to write proper commit messages.

1. Create a commit message helper script:
   ```python
   #!/usr/bin/env python3
   """
   Interactive commit message helper
   Usage: python3 commit_helper.py
   """
   import sys
   import re
   import subprocess
   
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
       
       def build_message(self):
           """Build complete commit message interactively"""
           print("🚀 Interactive Commit Message Builder")
           print("=" * 40)
           
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
       
       def commit_with_message(self, message):
           """Perform the actual commit"""
           try:
               result = subprocess.run(['git', 'commit', '-m', message], 
                                     capture_output=True, text=True, check=True)
               print("✅ Commit successful!")
               return True
           except subprocess.CalledProcessError as e:
               print(f"❌ Commit failed: {e.stderr}")
               return False
   
   def main():
       helper = CommitHelper()
       
       # Check if there are staged changes
       try:
           result = subprocess.run(['git', 'diff', '--cached', '--quiet'])
           if result.returncode != 0:
               # There are staged changes
               message = helper.build_message()
               
               confirm = input("\n🤔 Proceed with commit? (Y/n): ").strip().lower()
               if confirm in ['', 'y', 'yes']:
                   helper.commit_with_message(message)
               else:
                   print("Commit cancelled")
           else:
               print("❌ No staged changes found. Use 'git add' first.")
       except subprocess.CalledProcessError:
           print("❌ Not in a git repository")
   
   if __name__ == "__main__":
       main()
   ```

2. Make the helper executable and test it:
   ```bash
   chmod +x commit_helper.py
   
   # Stage some changes and run the helper
   echo "New feature" > new_feature.txt
   git add new_feature.txt
   python3 commit_helper.py
   ```

## Key Concepts

### Commit-msg Hook

- **Input**: Receives path to temporary file containing commit message
- **Modification**: Can modify the message by writing to the file
- **Blocking**: Exit code 1 prevents the commit
- **Timing**: Runs after message is entered but before commit is created

### Jira Integration Patterns

1. **Prefix Format**: `PROJ-123: Description`
2. **Bracket Format**: `[PROJ-123] Description`
3. **Inline Format**: `Description PROJ-123`
4. **Multiple Tickets**: `PROJ-123 PROJ-456: Description`

### Conventional Commits

Format: `type(scope)!: description`

- **type**: feat, fix, docs, style, refactor, perf, test, chore, build, ci
- **scope**: Optional, indicates area of change
- **!**: Indicates breaking change
- **description**: Brief description in imperative mood

### Message Structure Best Practices

1. **Subject Line**: Under 72 characters, imperative mood
2. **Blank Line**: Separate subject from body
3. **Body**: Wrap at 72 characters, explain what and why
4. **Footer**: Reference issues, breaking changes

## Troubleshooting

### Hook Not Triggering?
- Check file permissions: `chmod +x .git/hooks/commit-msg`
- Verify shebang line: `#!/usr/bin/env python3`
- Test hook manually: `.git/hooks/commit-msg test-message-file`

### Regex Not Matching?
- Test patterns interactively in Python
- Use online regex testers
- Start simple and add complexity gradually

### Configuration Not Loading?
- Check JSON syntax with `python3 -m json.tool .commit-config.json`
- Verify file permissions and location
- Add error handling for missing config

## Best Practices

1. **Clear Error Messages**: Help users understand what's wrong
2. **Flexible Patterns**: Support different team conventions
3. **Configuration**: Make rules configurable per project
4. **Performance**: Keep validation fast
5. **Backwards Compatibility**: Don't break existing workflows

## Next Steps

In Lab 4, you'll learn how to chain multiple hooks together and apply different rules based on the target branch.

## Summary

You've learned:
- How to implement commit message validation using the commit-msg hook
- How to enforce Jira ticket references in various formats
- How to validate conventional commit format
- How to create configurable validation rules
- How to build interactive tools to help users write better commit messages

Your commit messages are now standardized and trackable across your development workflow!