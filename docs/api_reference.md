# API Reference

This document provides detailed information about the Secure Wiki Automation Tool's API and how it interacts with MediaWiki-based wikis.

## Overview

The Secure Wiki Automation Tool communicates with MediaWiki-based wikis through their REST API endpoints. All communication is conducted over HTTPS for security.

## Core Components

### WikiConfigManager
Handles loading and managing wiki configurations from JSON files.

#### Methods
- `load_config()`: Load the main configuration file
- `load_user_config()`: Load the user configuration file
- `merge_configs()`: Merge main and user configurations
- `get_wiki_config(wiki_id)`: Get configuration for a specific wiki
- `get_wiki_list()`: Get a list of all available wikis
- `get_default_wiki()`: Get the default wiki ID
- `add_wiki(wiki_id, wiki_config)`: Add a new wiki to user configuration
- `validate_api_url(api_url)`: Validate that an API URL is properly formatted

### WikiSelector
Handles wiki selection and registration for the Secure Wiki Automation Tool.

#### Methods
- `select_wiki_interactive()`: Interactively select a wiki from available options
- `categorize_wikis(wiki_list)`: Categorize wikis for better presentation
- `handle_custom_url()`: Handle custom wiki URL input
- `handle_add_wiki()`: Handle adding a new wiki interactively

### WikiValidator
Handles configurable validation for different wiki styles.

#### Methods
- `fetch_wiki_page(wiki_api_url, page_title)`: Fetch content of a page from a wiki
- `read_local_file(file_path)`: Read content of a local file
- `check_wiki_specific_features(content, validation_rules)`: Check content for wiki-specific features
- `validate_submission(wiki_api_url, page_title, content_file, validation_rules)`: Validate submitted content
- `print_validation_report(success, validation_details, wiki_name)`: Print detailed validation report

### EnhancedSecureWikiBot
Main class for secure wiki submissions with enhanced features.

#### Methods
- `set_wiki_config(wiki_config)`: Set current wiki configuration
- `log_message(message)`: Log messages to file with timestamp
- `secure_clear_string(s)`: Securely clear string from memory
- `run_curl_command(data_params, method, expect_json, initial_cookies, urlencode_params)`: Execute curl commands
- `get_login_token()`: Get login token from Wiki API
- `login(login_token, password)`: Login to Wiki API
- `get_csrf_token()`: Get CSRF token for editing
- `submit_wiki_page(title, content, summary, csrf_token, is_bot_edit)`: Submit page content to Wiki
- `exponential_backoff(func, *args, max_retries, **kwargs)`: Execute function with exponential backoff
- `cleanup()`: Cleanup temporary files and clear sensitive data
- `submit_content(page_title, content_file, edit_summary)`: Main function to submit content

## MediaWiki API Endpoints

### Authentication

#### Login
```
POST /api.php HTTP/1.1
Host: wiki.example.com
Content-Type: application/x-www-form-urlencoded

action=login&lgname=username&lgpassword=password&lgtoken=token&format=json
```

**Parameters:**
- `action`: Must be "login"
- `lgname`: Username
- `lgpassword`: Password (URL-encoded)
- `lgtoken`: Login token (URL-encoded)
- `format`: Must be "json"

**Purpose**: Authenticate user credentials with the wiki.

#### Get Login Token
```
POST /api.php HTTP/1.1
Host: wiki.example.com
Content-Type: application/x-www-form-urlencoded

action=query&meta=tokens&type=login&format=json
```

**Parameters:**
- `action`: Must be "query"
- `meta`: Must be "tokens"
- `type`: Must be "login"
- `format`: Must be "json"

**Purpose**: Retrieve a login token required for authentication.

### Content Management

#### Get CSRF Token
```
POST /api.php HTTP/1.1
Host: wiki.example.com
Content-Type: application/x-www-form-urlencoded

action=query&meta=tokens&type=csrf&format=json
```

**Parameters:**
- `action`: Must be "query"
- `meta`: Must be "tokens"
- `type`: Must be "csrf"
- `format`: Must be "json"

**Purpose**: Retrieve CSRF token required for editing operations.

#### Edit Page
```
POST /api.php HTTP/1.1
Host: wiki.example.com
Content-Type: application/x-www-form-urlencoded

action=edit&title=PageTitle&text=PageContent&summary=EditSummary&token=csrftoken&format=json
```

**Parameters:**
- `action`: Must be "edit"
- `title`: Title of the page to edit
- `text`: Content of the page (URL-encoded)
- `summary`: Edit summary (URL-encoded)
- `token`: CSRF token (URL-encoded)
- `format`: Must be "json"
- `bot`: Optional, set to "1" for bot edits

**Purpose**: Create or modify wiki pages.

### Data Retrieval

#### Get Page Content
```
GET /api.php?action=query&titles=PageTitle&prop=revisions&rvprop=content&format=json HTTP/1.1
Host: wiki.example.com
```

**Parameters:**
- `action`: Must be "query"
- `titles`: Title of the page to retrieve
- `prop`: Must be "revisions"
- `rvprop`: Must be "content"
- `format`: Must be "json"

**Purpose**: Retrieve the content of a wiki page.

## Error Handling

### Common Error Codes

1. **badtoken**: CSRF token is invalid
   - Solution: Get a new CSRF token and retry

2. **maxlag**: Wiki is currently lagging
   - Solution: Wait and retry with exponential backoff

3. **spamdetected**: Content detected as spam
   - Solution: Review content for spam keywords

4. **abusefilter**: Content blocked by abuse filter
   - Solution: Review content for policy violations

5. **WrongToken**: Login token is invalid
   - Solution: Get a new login token and retry

### Retry Logic

The tool implements exponential backoff for transient errors:
- Initial delay: 1 second
- Multiplier: 2x for each retry
- Maximum retries: 3 attempts

## Rate Limiting

MediaWiki APIs typically implement rate limiting to prevent abuse. The tool respects these limits by:

1. Implementing exponential backoff for rate limit errors
2. Using appropriate delays between requests
3. Handling maxlag errors gracefully

## Session Management

The tool manages wiki sessions through:

1. **Cookie Storage**: Temporary cookie files for session persistence
2. **Token Management**: Proper handling of login and CSRF tokens
3. **Cleanup**: Automatic removal of temporary files after use

## Supported Features

### Wiki Compatibility
The tool works with wikis that have:
- MediaWiki 1.27 or later
- API module enabled
- Appropriate user permissions
- HTTPS support

### Internationalization
The tool supports international wikis:
- Works with wikis in any language
- No hardcoded language dependencies
- Proper UTF-8 encoding support

## Security Considerations

### HTTPS Requirements
All communication with wiki APIs must use HTTPS to ensure:
- Data encryption in transit
- Server authentication
- Protection against man-in-the-middle attacks

### Credential Protection
- Credentials are never stored in files
- Passwords are hidden during input
- Memory is securely cleared after use
- No logging of sensitive information

## Configuration Options

### Wiki Configuration Structure
```json
{
  "name": "Wiki Name",
  "api_url": "https://wiki.example.com/api.php",
  "user_agent": "Custom User Agent String",
  "validation_rules": {
    "rule_name": "pattern_to_match"
  }
}
```

### Validation Rules
Each wiki can define custom validation rules that are checked after submission:
- Pattern matching for specific wiki elements
- Custom validation functions
- Configurable rule sets

## Logging

### Log File Location
- `/tmp/wiki_submission_$$.log` (where $$ is the process ID)

### Log Content
- Timestamped entries for all operations
- Error messages and debugging information
- No sensitive data (passwords, tokens)

## Testing

### Test Coverage
The tool includes tests for:
- Configuration loading and merging
- Wiki selection and registration
- Validation rule checking
- API communication
- Error handling

### Testing Best Practices
- Test with multiple wiki platforms
- Verify security features work correctly
- Check error handling and recovery
- Validate configuration management