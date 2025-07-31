# Bash Automation Scripts Documentation

This document provides detailed information about the Bash automation scripts included in the Wiki Submission Tool.

## Overview

The Bash automation scripts provide a shell-based approach to programmatically submit content to MediaWiki-based wikis. These scripts offer both secure and standard automation options.

## Available Scripts

### 1. wiki_secure_submission.sh

The secure submission script that prompts for credentials during execution.

**Features**:
- Runtime credential entry
- Hidden password input
- Memory clearance after use
- Automatic cleanup of temporary files
- Error handling with retry mechanisms

**Usage**:
```bash
chmod +x wiki_secure_submission.sh
./wiki_secure_submission.sh "https://wiki.archlinux.org/api.php" "Page Title" "content_file.md" "Edit summary"
```

### 2. wiki_automated_submission.sh

The standard automation script that can use file-based or environment variable credentials.

**Features**:
- Configurable credential sources
- Batch processing capabilities
- Integration with CI/CD systems
- Error handling with retry mechanisms

**Usage**:
```bash
chmod +x wiki_automated_submission.sh
./wiki_automated_submission.sh "https://wiki.archlinux.org/api.php" "Page Title" "content_file.md" "Edit summary"
```

## Script Architecture

### Common Components

All Bash scripts share common components:

1. **Security Functions**:
   - `secure_clear()`: Clears sensitive variables from memory
   - `cleanup()`: Removes temporary files and clears credentials
   - `log_message()`: Logs operations to a temporary file

2. **API Interaction Functions**:
   - `run_curl_command()`: Executes curl requests with proper error handling
   - `get_login_token()`: Retrieves authentication tokens
   - `login()`: Authenticates with the wiki
   - `get_csrf_token()`: Retrieves CSRF tokens for editing
   - `submit_wiki_page()`: Submits content to wiki pages

3. **Error Handling Functions**:
   - `exponential_backoff()`: Implements retry logic with exponential delays
   - Error detection and reporting functions

### Security Implementation

#### Credential Handling
- Credentials entered at runtime, never stored
- Password input hidden using `read -rs`
- Variables securely cleared after use
- Temporary files automatically removed

#### File Security
- Temporary files use process ID for unique names
- File permissions restricted to owner only
- Files stored in `/tmp` directory
- Automatic cleanup on script exit

#### Communication Security
- All requests use HTTPS
- SSL certificate validation enabled
- User agent identification provided
- Request timeouts configured

### Error Handling

#### Retry Mechanism
The scripts implement exponential backoff for transient errors:

1. First retry: 1 second delay
2. Second retry: 2 second delay
3. Third retry: 4 second delay

#### Error Types
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

```bash
# wiki_credentials.conf
WIKI_API_URL=https://wiki.archlinux.org/api.php
WIKI_USERNAME=your_username
WIKI_PASSWORD=your_password
```

### Dependencies

#### Required Tools
- `bash`: Bash shell
- `curl`: HTTP client
- `openssl`: For secure operations
- `python3`: For JSON parsing

#### Installation (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install curl openssl python3
```

#### Installation (Arch Linux)
```bash
sudo pacman -Syu curl openssl python3
```

### Usage Examples

#### Secure Submission
```bash
# Make script executable
chmod +x wiki_secure_submission.sh

# Run with secure credential entry
./wiki_secure_submission.sh \
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
chmod +x wiki_automated_submission.sh

# Run without credential prompts
./wiki_automated_submission.sh \
  "My Project Documentation" \
  "docs/project_documentation.md" \
  "Adding documentation for my project"
```

#### Batch Processing
```bash
#!/bin/bash
# batch_submit.sh

# Configuration
WIKI_API_URL="https://wiki.archlinux.org/api.php"
CONTENT_DIR="./content"

# Process all markdown files
for file in "$CONTENT_DIR"/*.md; do
  # Extract page title from filename
  page_title=$(basename "$file" .md)
  
  # Submit to wiki
  ./wiki_automated_submission.sh \
    "$WIKI_API_URL" \
    "$page_title" \
    "$file" \
    "Automated batch update"
done
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
    
    - name: Install dependencies
      run: sudo apt-get install curl openssl python3
    
    - name: Update wiki
      env:
        WIKI_USERNAME: ${{ secrets.WIKI_USERNAME }}
        WIKI_PASSWORD: ${{ secrets.WIKI_PASSWORD }}
      run: |
        chmod +x scripts/wiki_automated_submission.sh
        ./scripts/wiki_automated_submission.sh \
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
    - chmod +x scripts/wiki_automated_submission.sh
    - ./scripts/wiki_automated_submission.sh \
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

1. **Permission Denied**
   ```bash
   chmod +x script_name.sh
   ```

2. **Command Not Found**
   ```bash
   # Install dependencies
   sudo apt-get install curl openssl python3
   ```

3. **SSL Certificate Error**
   ```bash
   # Update certificates
   sudo apt-get update && sudo apt-get upgrade ca-certificates
   ```

4. **Invalid Credentials**
   - Verify username and password
   - Check account permissions
   - Confirm wiki API endpoint

#### Debugging

Enable verbose logging by modifying the script:
```bash
# Uncomment for debugging
# set -x
```

Check temporary log files:
```bash
# Log file location
/tmp/wiki_submission_$$.log
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

### Customization

#### Adding New Features
1. Create new functions for additional functionality
2. Follow existing error handling patterns
3. Add appropriate logging
4. Update documentation

#### Modifying Behavior
1. Adjust timeout values as needed
2. Modify retry logic parameters
3. Change temporary file locations
4. Update user agent strings

### Limitations

#### Known Issues
1. Requires Python 3 for JSON parsing
2. Limited to MediaWiki-based wikis
3. No built-in content validation
4. No GUI interface

#### Future Enhancements
1. Add content validation features
2. Implement GUI interface
3. Support additional wiki platforms
4. Add more comprehensive testing

### Contributing

#### Development Setup
1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Test thoroughly
5. Submit a pull request

#### Code Standards
1. Follow existing code style
2. Add comments for complex logic
3. Include error handling
4. Update documentation