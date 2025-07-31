# Python Automation Scripts Documentation

This document provides detailed information about the Python automation scripts included in the Wiki Submission Tool.

## Overview

The Python automation scripts provide a robust, feature-rich approach to programmatically submit content to MediaWiki-based wikis. These scripts offer both secure and standard automation options with enhanced error handling and extensibility.

## Available Scripts

### 1. wiki_secure_submission.py

The secure submission script that prompts for credentials during execution.

**Features**:
- Runtime credential entry
- Hidden password input using getpass
- Memory clearance after use with secure overwrite
- Automatic cleanup of temporary files
- Comprehensive error handling with retry mechanisms
- Type hints for better code clarity
- Detailed logging

**Usage**:
```bash
chmod +x wiki_secure_submission.py
python3 wiki_secure_submission.py "https://wiki.archlinux.org/api.php" "Page Title" "content_file.md" "Edit summary"
```

### 2. wiki_automated_submission.py

The standard automation script that can use file-based or environment variable credentials.

**Features**:
- Configurable credential sources
- Batch processing capabilities
- Integration with CI/CD systems
- Comprehensive error handling with retry mechanisms
- Object-oriented design for extensibility
- Detailed logging and debugging

**Usage**:
```bash
chmod +x wiki_automated_submission.py
python3 wiki_automated_submission.py "https://wiki.archlinux.org/api.php" "Page Title" "content_file.md" "Edit summary"
```

## Script Architecture

### Class Structure

#### SecureWikiBot
The main class for secure wiki submissions:

```python
class SecureWikiBot:
    def __init__(self):
        self.username = None
        self.log_file = f"/tmp/wiki_submission_{os.getpid()}.log"
        self.session = None
```

**Key Methods**:
- `submit_content()`: Main entry point for content submission
- `get_login_token()`: Retrieves authentication tokens
- `login()`: Authenticates with the wiki
- `get_csrf_token()`: Retrieves CSRF tokens for editing
- `submit_wiki_page()`: Submits content to wiki pages
- `exponential_backoff()`: Implements retry logic with exponential delays
- `cleanup()`: Removes temporary files and clears credentials

#### StandardWikiBot
The main class for standard wiki submissions with configurable credentials.

### Security Implementation

#### Credential Handling
- Credentials entered at runtime using getpass, never stored
- Password input hidden during entry
- Variables securely cleared after use with multiple overwrite passes
- Temporary files automatically removed

#### Memory Security
```python
def secure_clear_string(self, s: str) -> None:
    """Securely clear a string from memory by overwriting with random data."""
    if s:
        # Overwrite with random data multiple times
        for _ in range(3):
            random_data = secrets.token_hex(len(s))
            s = random_data
        # Clear the random data
        del s
```

#### File Security
- Temporary files use process ID for unique names
- File permissions restricted to owner only
- Files stored in `/tmp` directory
- Automatic cleanup using context managers and signal traps

#### Communication Security
- All requests use HTTPS
- SSL certificate validation enabled
- User agent identification provided
- Request timeouts configured
- URL encoding for sensitive parameters

### Error Handling

#### Exception Handling
The scripts use comprehensive exception handling:

```python
try:
    # API operations
    response = self.run_curl_command(...)
except Exception as e:
    # Error handling and logging
    self.log_message(f"Error occurred: {e}")
    raise
```

#### Retry Mechanism
The scripts implement exponential backoff for transient errors:

```python
def exponential_backoff(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
    retry_count = 0
    delay = 1
    
    while retry_count < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                # Check if this is a transient error
                if any(keyword in str(e).lower() for keyword in ["maxlag", "timeout", "network"]):
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
                else:
                    # Non-transient error, don't retry
                    raise
    return None
```

#### Specific Error Types
- **Authentication Errors**: Invalid credentials or tokens
- **Network Errors**: Connection timeouts or DNS failures
- **API Errors**: Server-side issues or rate limiting
- **Content Errors**: Invalid wiki markup or spam detection

### Configuration

#### Environment Variables
The scripts can use environment variables for configuration:

- `WIKI_API_URL`: Wiki API endpoint URL
- `WIKI_USERNAME`: Wiki username
- `WIKI_PASSWORD`: Wiki password

#### Configuration Files
The scripts can use configuration files:

```python
# wiki_credentials.conf
WIKI_API_URL=https://wiki.archlinux.org/api.php
WIKI_USERNAME=your_username
WIKI_PASSWORD=your_password
```

### Dependencies

#### Required Packages
- `python3`: Python 3.6+
- `subprocess`: For executing curl commands
- `json`: For JSON parsing
- `argparse`: For command-line argument parsing
- `getpass`: For secure password input
- `secrets`: For secure random data generation

#### Installation
```bash
# No additional packages required beyond standard library
# All dependencies are part of Python standard library
```

### Usage Examples

#### Secure Submission
```bash
# Make script executable
chmod +x wiki_secure_submission.py

# Run with secure credential entry
python3 wiki_secure_submission.py \
  "https://wiki.archlinux.org/api.php" \
  "My Project Documentation" \
  "docs/project_documentation.md" \
  "Adding documentation for my project"
```

#### Automated Submission with Environment Variables
```bash
# Set environment variables
export WIKI_API_URL="https://wiki.archlinux.org/api.php"
export WIKI_USERNAME="my_username"
export WIKI_PASSWORD="my_password"

# Make script executable
chmod +x wiki_automated_submission.py

# Run without credential prompts
python3 wiki_automated_submission.py \
  "My Project Documentation" \
  "docs/project_documentation.md" \
  "Adding documentation for my project"
```

#### Batch Processing
```python
#!/usr/bin/env python3
# batch_submit.py

import os
import glob
from wiki_automated_submission import StandardWikiBot

# Configuration
WIKI_API_URL = "https://wiki.archlinux.org/api.php"
CONTENT_DIR = "./content"

# Initialize bot
bot = StandardWikiBot()

# Process all markdown files
for file_path in glob.glob(os.path.join(CONTENT_DIR, "*.md")):
    # Extract page title from filename
    page_title = os.path.basename(file_path).replace(".md", "")
    
    # Submit to wiki
    try:
        bot.submit_content(WIKI_API_URL, page_title, file_path, "Automated batch update")
        print(f"Successfully submitted {page_title}")
    except Exception as e:
        print(f"Failed to submit {page_title}: {e}")
```

### Integration with CI/CD

#### GitHub Actions
```yaml
# .github/workflows/wiki-update.yml
name: Update Wiki
on:
  push:
    branches: [ main ]

jobs:
  update-wiki:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Update wiki
      env:
        WIKI_USERNAME: ${{ secrets.WIKI_USERNAME }}
        WIKI_PASSWORD: ${{ secrets.WIKI_PASSWORD }}
      run: |
        chmod +x scripts/wiki_automated_submission.py
        python3 scripts/wiki_automated_submission.py \
          "https://wiki.archlinux.org/api.php" \
          "Project Documentation" \
          "docs/documentation.md" \
          "Automated update from CI/CD"
```

#### GitLab CI
```yaml
# .gitlab-ci.yml
wiki-update:
  stage: deploy
  script:
    - chmod +x scripts/wiki_automated_submission.py
    - python3 scripts/wiki_automated_submission.py \
        "https://wiki.archlinux.org/api.php" \
        "Project Documentation" \
        "docs/documentation.md" \
        "Automated update from CI/CD"
  only:
    - main
  variables:
    WIKI_USERNAME: $WIKI_USERNAME
    WIKI_PASSWORD: $WIKI_PASSWORD
```

### Troubleshooting

#### Common Issues

1. **Python Not Found**
   ```bash
   # Install Python 3
   sudo apt-get install python3
   ```

2. **Permission Denied**
   ```bash
   chmod +x script_name.py
   ```

3. **Import Errors**
   ```bash
   # All dependencies are part of standard library
   # No additional packages required
   ```

4. **SSL Certificate Error**
   ```bash
   # Update certificates
   sudo apt-get update && sudo apt-get upgrade ca-certificates
   ```

5. **Invalid Credentials**
   - Verify username and password
   - Check account permissions
   - Confirm wiki API endpoint

#### Debugging

Enable verbose logging by checking temporary log files:
```bash
# Log file location
/tmp/wiki_submission_$$.log
```

Add debug print statements to the script:
```python
# Add for debugging
print(f"Debug: Variable value is {variable}")
```

### Best Practices

#### Security
1. Never commit credentials to version control
2. Use secure file permissions (chmod 600) for credential files
3. Run scripts in secure environments
4. Monitor for unauthorized changes

#### Performance
1. Minimize API requests
2. Implement appropriate delays between operations
3. Handle errors gracefully
4. Log operations for audit purposes

#### Reliability
1. Test scripts thoroughly before deployment
2. Implement error handling and retry logic
3. Monitor for rate limiting
4. Validate content before submission

#### Code Quality
1. Use type hints for better code clarity
2. Follow PEP 8 style guidelines
3. Add docstrings for functions and classes
4. Write unit tests for critical functions

### Customization

#### Adding New Features
1. Create new methods in the WikiBot classes
2. Follow existing error handling patterns
3. Add appropriate logging
4. Update documentation

#### Modifying Behavior
1. Adjust timeout values in curl commands
2. Modify retry logic parameters
3. Change temporary file locations
4. Update user agent strings

#### Extending Functionality
1. Add new API endpoint support
2. Implement content validation
3. Add support for file uploads
4. Create GUI interface

### Limitations

#### Known Issues
1. Limited to MediaWiki-based wikis
2. No built-in content validation
3. No GUI interface
4. Requires curl for HTTP operations

#### Future Enhancements
1. Add content validation features
2. Implement GUI interface
3. Support additional wiki platforms
4. Add more comprehensive testing
5. Implement asynchronous operations

### Contributing

#### Development Setup
1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Test thoroughly
5. Submit a pull request

#### Code Standards
1. Follow PEP 8 style guidelines
2. Use type hints where appropriate
3. Write docstrings for functions and classes
4. Add comments for complex logic
5. Include error handling
6. Update documentation

#### Testing
1. Test with multiple wiki platforms
2. Verify security features work correctly
3. Check error handling for various scenarios
4. Validate credential handling security

### API Reference

#### SecureWikiBot Class

**Methods**:
- `__init__()`: Initialize the bot
- `log_message(message: str)`: Log messages to file
- `secure_clear_string(s: str)`: Securely clear string from memory
- `run_curl_command(wiki_api_url: str, data_params: Dict[str, str], ...)`: Execute curl commands
- `get_login_token(wiki_api_url: str)`: Get login token from API
- `login(wiki_api_url: str, login_token: str, password: str)`: Authenticate with wiki
- `get_csrf_token(wiki_api_url: str)`: Get CSRF token for editing
- `submit_wiki_page(wiki_api_url: str, title: str, content: str, ...)`: Submit page content
- `exponential_backoff(func, *args, max_retries: int = 3, ...)`: Retry function with exponential backoff
- `cleanup()`: Clean up temporary files and credentials
- `submit_content(wiki_api_url: str, page_title: str, content_file: str, ...)`: Main submission function

#### StandardWikiBot Class

Similar to SecureWikiBot but with additional methods for credential loading from files or environment variables.

### Command Line Interface

#### Arguments
1. `wiki_api_url`: Wiki API endpoint URL
2. `page_title`: Title of the page to edit
3. `content_file`: Path to file containing content
4. `edit_summary`: Optional edit summary

#### Options
- `--help`: Show help message
- No additional options in current implementation

### Logging

#### Log Format
```
[YYYY-MM-DD HH:MM:SS UTC] Log message
```

#### Log Location
```
/tmp/wiki_submission_$$.log
```

#### Log Content
- Operation timestamps
- Function entry/exit
- Error conditions
- Debug information (sensitive data excluded)