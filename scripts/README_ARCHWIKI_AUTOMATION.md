# Arch Wiki Automation Scripts

This directory contains scripts to automate the submission of content to the Arch Wiki using the MediaWiki API.

## Overview

The automation process consists of three main scripts:
1. `archwiki_api_login.sh` - Handles authentication with the Arch Wiki
2. `archwiki_get_csrf_token.sh` - Retrieves the CSRF token needed for editing
3. `archwiki_submit_edit.sh` - Submits edits to Arch Wiki pages

These scripts can be orchestrated using the master script `archwiki_automated_submission.sh`.

## Prerequisites

1. **curl** - Command-line tool for making HTTP requests
2. **bash** - Bourne Again SHell for running the scripts
3. **Arch Wiki Account** - A registered account with editing permissions

## Setup

### 1. Create Credentials File

Create a file named `archwiki_credentials.conf` in the project root directory with your Arch Wiki credentials:

```bash
USERNAME=your_username
PASSWORD=your_password
```

**Security Note:** Never commit this file to version control. It should be added to `.gitignore`.

### 2. Make Scripts Executable

```bash
chmod +x scripts/archwiki_api_login.sh
chmod +x scripts/archwiki_get_csrf_token.sh
chmod +x scripts/archwiki_submit_edit.sh
chmod +x scripts/archwiki_automated_submission.sh
```

## Usage

### Automated Submission (Recommended)

Use the master script to handle the entire process:

```bash
./scripts/archwiki_automated_submission.sh "Bluetooth" "archwiki_submission_content.md" "Add troubleshooting section for Realtek Bluetooth authentication failures"
```

### Manual Process

If you prefer to run each step manually:

1. **Login:**
   ```bash
   ./scripts/archwiki_api_login.sh
   ```

2. **Get CSRF Token:**
   ```bash
   ./scripts/archwiki_get_csrf_token.sh
   ```

3. **Submit Edit:**
   ```bash
   ./scripts/archwiki_submit_edit.sh "Bluetooth" "archwiki_submission_content.md" "Add troubleshooting section for Realtek Bluetooth authentication failures"
   ```

## Script Details

### archwiki_api_login.sh

Handles authentication with the Arch Wiki API:
- Obtains a login token
- Performs login with username and password
- Stores session cookies in `/tmp/archwiki_cookies.txt`

### archwiki_get_csrf_token.sh

Retrieves the CSRF token required for editing:
- Uses existing session cookies
- Stores CSRF token in `/tmp/archwiki_csrf_token.txt`

### archwiki_submit_edit.sh

Submits edits to Arch Wiki pages:
- Requires page title, content file, and edit summary
- Uses CSRF token and session cookies for authentication
- Returns success or error response

### archwiki_automated_submission.sh

Master script that orchestrates the entire process:
- Runs login, CSRF token retrieval, and edit submission in sequence
- Handles error checking and cleanup of temporary files
- Provides colored output for better user experience

## Error Handling

All scripts include basic error handling:
- Check for required files and credentials
- Validate API responses
- Provide meaningful error messages
- Exit with appropriate error codes

## Security Considerations

1. **Credentials File**: Store your credentials securely and never commit to version control
2. **Temporary Files**: Session cookies and CSRF tokens are stored in `/tmp/` and cleaned up after use
3. **HTTPS**: All communication with Arch Wiki uses HTTPS

## Troubleshooting

### Common Issues

1. **Login Failed**: Check your credentials in `archwiki_credentials.conf`
2. **CSRF Token Error**: Ensure you're logged in before getting the CSRF token
3. **Edit Failed**: Check that your account has editing permissions
4. **Permission Denied**: Ensure scripts are executable (`chmod +x`)

### Debugging

To see detailed output from curl commands, add `-v` flag to curl commands in the scripts.

## API Documentation

These scripts use the MediaWiki Action API:
- Login: https://www.mediawiki.org/wiki/API:Login
- Tokens: https://www.mediawiki.org/wiki/API:Tokens
- Edit: https://www.mediawiki.org/wiki/API:Edit

## Contributing

Feel free to improve these scripts by:
1. Adding more robust error handling
2. Supporting additional MediaWiki API features
3. Improving the user interface
4. Adding support for other wikis

## License

These scripts are provided as part of the Linux Bluetooth Troubleshooting project under the MIT License.