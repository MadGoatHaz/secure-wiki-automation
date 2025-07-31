# Usage Guide

This guide provides detailed instructions on how to use the Secure Wiki Automation Tool for submitting content to MediaWiki-based wikis.

## Installation

### Prerequisites
- Python 3.6 or later
- pip (Python package installer)
- curl (for API communication)
- Internet connection

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/secure-wiki-automation.git
   cd secure-wiki-automation
   ```

2. Install required dependencies:
   ```bash
   pip install requests
   ```

3. Verify installation:
   ```bash
   python3 scripts/wiki_secure_submission.py --help
   ```

## Basic Usage

### Command Structure
```bash
python3 scripts/wiki_secure_submission.py [OPTIONS] PAGE_TITLE CONTENT_FILE [EDIT_SUMMARY]
```

### Required Arguments
- `PAGE_TITLE`: The title of the wiki page to edit
- `CONTENT_FILE`: Path to the file containing the content to submit

### Optional Arguments
- `EDIT_SUMMARY`: Edit summary for the wiki edit (defaults to "Automated update for wiki content")

### Options
- `--select-wiki`: Interactively select a wiki from the configuration
- `--wiki WIKI_ID`: Specify a wiki by ID from the configuration
- `--api-url API_URL`: Specify a custom wiki API URL
- `--add-wiki`: Interactively add a new wiki to the configuration
- `--help`: Show help message and exit

## Wiki Selection Methods

### 1. Interactive Selection
Use the `--select-wiki` option to choose from a list of predefined wikis:

```bash
python3 scripts/wiki_secure_submission.py --select-wiki "My Page" "content.md" "Initial page creation"
```

This will display a categorized list of available wikis:
- Wikimedia Foundation Wikis
- Technology Wikis
- Fandom Wikis
- Other Wikis

Additional options:
- Custom Wiki URL
- Add New Wiki

### 2. Direct Selection by ID
Use the `--wiki` option with a wiki ID to directly select a wiki:

```bash
python3 scripts/wiki_secure_submission.py --wiki archwiki "My Page" "content.md" "Update"
```

Available wiki IDs can be found in `wiki_config.json`.

### 3. Custom API URL
Use the `--api-url` option to specify a custom wiki API URL:

```bash
python3 scripts/wiki_secure_submission.py --api-url "https://mywiki.example.com/api.php" "My Page" "content.md" "Update"
```

### 4. Adding New Wikis
Use the `--add-wiki` option to interactively add a new wiki:

```bash
python3 scripts/wiki_secure_submission.py --add-wiki "My Page" "content.md" "Update"
```

This will prompt for:
- Wiki ID (unique identifier)
- Wiki name
- API URL
- User agent string (optional)

## Configuration

### Main Configuration File
`wiki_config.json` contains predefined configurations for popular wikis:

```json
{
  "default_wiki": "archwiki",
  "wikis": {
    "archwiki": {
      "name": "Arch Wiki",
      "api_url": "https://wiki.archlinux.org/api.php",
      "user_agent": "WikiSecureBot/1.0 (Arch Wiki)",
      "validation_rules": {
        "related_articles": "{{Related articles",
        "subsection_format": "===",
        "note_box": "{{Note|"
      }
    }
  }
}
```

### User Configuration File
`user_wikis.json` allows users to define custom wikis:

1. Copy the sample file:
   ```bash
   cp user_wikis.json.sample user_wikis.json
   ```

2. Edit `user_wikis.json`:
   ```json
   {
     "wikis": {
       "my_custom_wiki": {
         "name": "My Custom Wiki",
         "api_url": "https://mywiki.example.com/api.php",
         "user_agent": "WikiSecureBot/1.0 (My Custom Wiki)",
         "validation_rules": {
           "custom_rule_1": "Custom validation pattern 1"
         }
       }
     }
   }
   ```

3. Use your custom wiki:
   ```bash
   python3 scripts/wiki_secure_submission.py --wiki my_custom_wiki "Page Title" "content.md" "Edit summary"
   ```

## Content Preparation

### File Format
The content file can be in any text format supported by the target wiki:
- Markdown (for wikis that support it)
- Wikitext (standard MediaWiki format)
- Plain text
- HTML (if supported by the wiki)

### Best Practices
1. Ensure content is properly formatted for the target wiki
2. Use appropriate wiki markup for headings, lists, links, etc.
3. Include relevant categories and templates
4. Follow the wiki's style guide
5. Test with a sandbox page before editing live content

### Example Content File
```wikitext
== Introduction ==
This is an example page for the Secure Wiki Automation Tool.

== Features ==
* Secure credential handling
* Multi-wiki support
* Configurable validation
* Intuitive interface

== Usage ==
See the [[Usage Guide]] for detailed instructions.

[[Category:Automation]]
[[Category:Security]]
```

## Security Features

### Credential Handling
1. Credentials are prompted during execution
2. Password input is hidden
3. Credentials are immediately cleared from memory
4. No logging of sensitive information

### Communication Security
1. All API communication uses HTTPS
2. Temporary files use process-specific names
3. User agent strings identify the tool properly

### Configuration Security
1. User configuration files should use secure permissions (600)
2. API URLs are validated for HTTPS
3. No sensitive data stored in configuration files

## Validation

### Post-Submission Validation
After submitting content, the tool automatically validates the submission:

1. **Content Matching**: Verifies the uploaded content matches the local file
2. **Wiki-Specific Features**: Checks for wiki-specific formatting elements
3. **Detailed Reporting**: Provides color-coded success/failure indicators

### Validation Rules
Each wiki can define custom validation rules in its configuration:

```json
"validation_rules": {
  "related_articles": "{{Related articles",
  "subsection_format": "===",
  "note_box": "{{Note|"
}
```

### Validation Report
The tool provides a detailed validation report:
```
[VALIDATION] Validation report for Arch Wiki:
✓ Content matches between local file and wiki page
[VALIDATION] Wiki-specific features check:
  ✓ related_articles
  ✓ subsection_format
  ✓ note_box
[VALIDATION SUCCESS] Validation successful for Arch Wiki!
```

## Error Handling

### Common Errors and Solutions

1. **Authentication Failed**
   - Verify username and password
   - Check if two-factor authentication is enabled
   - Ensure account has edit permissions

2. **CSRF Token Invalid**
   - The tool automatically retries with a new token
   - If persistent, check wiki API status

3. **Wiki Lagging**
   - The tool implements exponential backoff
   - Try again later if the issue persists

4. **Spam Detected**
   - Review content for spam keywords
   - Ensure content follows wiki guidelines

5. **Abuse Filter Blocked**
   - Review content for policy violations
   - Contact wiki administrators if needed

### Logging
The tool creates detailed logs in `/tmp/wiki_submission_$$.log` where `$$` is the process ID. These logs contain:
- Timestamped entries for all operations
- Error messages and debugging information
- No sensitive data (passwords, tokens)

## Advanced Usage

### Batch Processing
To submit multiple pages, create a script:

```bash
#!/bin/bash
pages=("Page1.md" "Page2.md" "Page3.md")
titles=("Page 1" "Page 2" "Page 3")

for i in "${!pages[@]}"; do
    python3 scripts/wiki_secure_submission.py --wiki archwiki "${titles[$i]}" "${pages[$i]}" "Batch update"
    sleep 5  # Wait between submissions
done
```

### Environment Integration
The tool can be integrated into:
- Continuous Integration (CI) pipelines
- Version control system hooks
- Automated documentation systems
- Content management workflows

### Custom Validation
To add custom validation rules for your wiki:
1. Add rules to the wiki configuration in `user_wikis.json`:
   ```json
   "validation_rules": {
     "custom_template": "{{CustomTemplate",
     "specific_category": "[[Category:MyCategory]]"
   }
   ```

2. The tool will automatically check for these patterns during validation

## Troubleshooting

### Common Issues

1. **Module Not Found Error**
   - Solution: Install required dependencies with `pip install requests`

2. **Permission Denied Error**
   - Solution: Ensure the script has execute permissions: `chmod +x scripts/wiki_secure_submission.py`

3. **Invalid API URL**
   - Solution: Verify the URL starts with `https://` and ends with `/api.php`

4. **Wiki Not Found**
   - Solution: Check if the wiki ID exists in the configuration files

### Getting Help
1. Check the documentation files in the `docs/` directory
2. Run the script with `--help` for usage information
3. Check the log files in `/tmp/` for detailed error information
4. Report issues on the project's GitHub repository

## Best Practices

### For Content Creators
1. Always preview content in a sandbox before submitting to live pages
2. Use descriptive edit summaries
3. Follow the target wiki's style guide
4. Test with different wiki platforms if needed

### For System Administrators
1. Regularly update the tool to benefit from security improvements
2. Monitor logs for unusual activity
3. Ensure proper file permissions for configuration files
4. Educate users on secure credential handling

### For Developers
1. Follow the contribution guidelines in `CONTRIBUTING.md`
2. Write tests for new features
3. Document code changes
4. Review security considerations in `SECURITY_GUIDE.md`

## Examples

### Submit to Arch Wiki
```bash
python3 scripts/wiki_secure_submission.py --wiki archwiki "My Page" "content.md" "Initial page creation"
```

### Submit to Wikipedia
```bash
python3 scripts/wiki_secure_submission.py --wiki wikipedia "My Article" "article.md" "New article submission"
```

### Submit to Custom Wiki
```bash
python3 scripts/wiki_secure_submission.py --api-url "https://mywiki.example.com/api.php" "My Page" "content.md" "Update"
```

### Interactive Wiki Selection
```bash
python3 scripts/wiki_secure_submission.py --select-wiki "My Page" "content.md" "Edit summary"
```

### Add New Wiki
```bash
python3 scripts/wiki_secure_submission.py --add-wiki "My Page" "content.md" "Edit summary"