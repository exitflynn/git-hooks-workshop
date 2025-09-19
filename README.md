## What are Git Hooks?

Like many other Version Control Systems, Git has a way to fire off custom scripts when certain important actions occur. There are two groups of these hooks: client-side and server-side. Client-side hooks are triggered by operations such as committing and merging, while server-side hooks run on network operations such as receiving pushed commits.

## Workshop Structure

This workshop consists of 8 progressive labs, each building upon the previous one:

### Lab 0: Basic Hooks Setup
- Remove `.sample` extensions from default hooks
- Understand the hooks directory structure
- Run your first basic hooks

### Lab 1: Hello World & Exit Codes
- Create a simple "Hello World" printing hook
- Learn about exit codes and how they control Git behavior
- Implement blocking hooks based on exit codes

### Lab 2: Linter Implementation
- Write a manual linting script in Python
- Integrate code quality checks into your Git workflow
- Handle linting errors and warnings

### Lab 3: Commit Message Validation
- Ensure commit messages contain Jira ticket references
- **Stretch Goal**: Implement conventional commit format validation
- Prevent commits with invalid messages

### Lab 4: Chaining Hooks & Branch-Specific Logic
- Combine multiple hooks into a workflow
- Apply hooks only to specific branches
- Build conditional logic into your hooks

### Lab 5: Post-Checkout Dependencies
- Automatically install dependencies after checkout
- Handle different dependency managers (pip, npm, etc.)
- Ensure development environment consistency

### Lab 6: Pre-commit Framework
- Introduction to the pre-commit framework
- Install and configure linters using pre-commit
- Leverage community-maintained hooks

### Lab 7: GitLeaks Secret Scanning
- Extend pre-commit setup with secret detection
- Prevent sensitive data from entering your repository
- Configure GitLeaks for your project needs

### Lab 8: Custom Auto-typing Hook
- Build a custom auto-typing correction program
- Export your custom tool as a pre-commit hook
- Share and distribute custom hooks

## Prerequisites

- Basic knowledge of Git commands
- Python 3.7+ installed
- A terminal/command line interface
- Your favorite text editor

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd git-hooks-workshop
   ```

2. Ensure Python 3.7+ is installed:
   ```bash
   python3 --version
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Navigate to Lab 0 to get started:
   ```bash
   cd lab0-basic-hooks
   ```

## Workshop Format

Each lab contains:
- **README.md**: Detailed instructions and learning objectives
- **solutions/**: Complete working examples
- **starter-files/**: Template files to get you started (where applicable)

## Getting Help

- Check the `solutions/` directory in each lab if you get stuck
- Review the main concepts in this README
- Each lab's README contains troubleshooting tips

## Learning Objectives

By the end of this workshop, you will be able to:
- Understand the different types of Git hooks and when to use them
- Write custom hooks in Python to enforce project policies
- Use exit codes effectively to control Git operations
- Implement code quality checks in your development workflow
- Use the pre-commit framework for advanced hook management
- Integrate secret scanning and security checks
- Create and distribute custom hooks for your team

## Resources

- [Official Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Pre-commit Framework](https://pre-commit.com/)
- [GitLeaks Documentation](https://github.com/zricethezav/gitleaks)

Let's get started with Lab 0!