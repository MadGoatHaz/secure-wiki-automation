# Troubleshooting Guide

This guide provides solutions to common issues you may encounter when using the Secure Wiki Automation Tool.

## Common Issues and Solutions

### 1. Authentication Problems

#### Issue: Login failed with "Invalid username or password"
**Possible Causes:**
- Incorrect username or password
- Two-factor authentication enabled
- Account locked or disabled
- Wiki-specific authentication requirements

**Solutions:**
1. Double-check your username and password
2. If you have two-factor authentication enabled, you may need to use an application password
3. Verify your account is active and has edit permissions
4. Check the wiki's authentication documentation for special requirements

#### Issue: Login failed with "WrongToken"
**Possible Causes:**
- Expired or invalid login token
- Network issues causing token corruption
- Wiki server issues

**Solutions:**
1. The tool automatically retries with a fresh token, but if it persists:
2. Check your network connection
3. Try again later if the wiki is experiencing issues
4. Verify the wiki API is functioning properly

### 2. Content Submission Issues

#### Issue: Edit failed with "badtoken"
**Possible Causes:**
- Expired or invalid CSRF token
- Session timeout
- Wiki server issues

**Solutions:**
1. The tool automatically retries with a fresh token
2. If the issue persists, try again later
3. Check if the wiki is experiencing technical issues

#### Issue: Edit failed with "maxlag"
**Possible Causes:**
- Wiki server is lagging
- High server load
- Database replication delays

**Solutions:**
1. The tool implements exponential backoff for this error
2. Try again later when server load is lower
3. Consider submitting during off-peak hours

#### Issue: Edit failed with "spamdetected"
**Possible Causes:**
- Content contains spam keywords
- External links flagged as spam
- Content matches spam patterns

**Solutions:**
1. Review your content for spam keywords
2. Remove or modify external links if possible
3. Simplify complex formatting that might trigger spam filters
4. Contact wiki administrators if you believe the content was incorrectly flagged

#### Issue: Edit failed with "abusefilter"
**Possible Causes:**
- Content violates wiki policies
- Triggers abuse filter rules
- Automated edit restrictions

**Solutions:**
1. Review your content for policy violations
2. Simplify formatting that might trigger filters
3. Contact wiki administrators for more information about the specific filter
4. Consider making edits manually if automated edits are restricted

### 3. Configuration Issues

#### Issue: Wiki not found in configuration
**Possible Causes:**
- Incorrect wiki ID
- Wiki not added to configuration
- Configuration file not loaded properly

**Solutions:**
1. Verify the wiki ID is correct (check `wiki_config.json` and `user_wikis.json`)
2. Add the wiki to your user configuration if needed
3. Ensure configuration files are in the correct location

#### Issue: Invalid API URL
**Possible Causes:**
- URL doesn't start with "https://"
- URL doesn't end with "/api.php"
- Wiki server is unreachable

**Solutions:**
1. Verify the API URL format: `https://wiki.example.com/api.php`
2. Test the URL in a web browser to ensure it's accessible
3. Check your network connection
4. Verify the wiki server is operational

### 4. Network and Connectivity Issues

#### Issue: Connection timeout
**Possible Causes:**
- Poor network connection
- Firewall blocking requests
- Wiki server is down
- DNS resolution issues

**Solutions:**
1. Check your network connection
2. Verify firewall settings allow outgoing HTTPS connections
3. Try accessing the wiki in a web browser
4. Check DNS settings
5. Try using a different network

#### Issue: SSL/TLS certificate errors
**Possible Causes:**
- Expired or invalid SSL certificate
- Corporate firewall intercepting HTTPS traffic
- System time not synchronized

**Solutions:**
1. Verify system time is correct
2. Check if corporate firewall is interfering with SSL
3. Update system certificates
4. Contact network administrator if using corporate network

### 5. File and Permission Issues

#### Issue: Permission denied when reading content file
**Possible Causes:**
- Insufficient file permissions
- File is locked by another process
- File doesn't exist

**Solutions:**
1. Verify file permissions: `ls -l content_file.md`
2. Ensure the file exists: `ls -l content_file.md`
3. Check if another process is using the file
4. Move the file to a location with appropriate permissions

#### Issue: Permission denied when creating temporary files
**Possible Causes:**
- Insufficient permissions in `/tmp` directory
- `/tmp` directory is full
- Disk space is full

**Solutions:**
1. Check permissions on `/tmp`: `ls -ld /tmp`
2. Check available disk space: `df -h /tmp`
3. Clear space in `/tmp` if needed
4. Consider changing the temporary directory location

### 6. Python and Dependency Issues

#### Issue: Module not found errors
**Possible Causes:**
- Missing Python dependencies
- Incorrect Python version
- Virtual environment issues

**Solutions:**
1. Install required dependencies: `pip install requests`
2. Verify Python version: `python3 --version` (requires 3.6 or later)
3. If using a virtual environment, ensure it's activated
4. Reinstall dependencies if they appear corrupted

#### Issue: Syntax errors when running script
**Possible Causes:**
- Incompatible Python version
- Corrupted script file
- Missing script permissions

**Solutions:**
1. Verify Python version: `python3 --version` (requires 3.6 or later)
2. Re-download or restore the script file
3. Ensure script has execute permissions: `chmod +x scripts/wiki_secure_submission.py`

## Debugging Steps

### 1. Enable Verbose Logging
Check the log file for detailed information:
```bash
# Find the log file (uses process ID)
ls -l /tmp/wiki_submission_*.log

# View the log content
cat /tmp/wiki_submission_*.log
```

### 2. Test Wiki Connectivity
Verify the wiki API is accessible:
```bash
curl -s "https://wiki.example.com/api.php?action=query&meta=siteinfo&format=json" | jq
```

### 3. Validate Configuration Files
Check JSON syntax in configuration files:
```bash
# Check main configuration
python3 -m json.tool wiki_config.json

# Check user configuration
python3 -m json.tool user_wikis.json
```

### 4. Test Individual Components
Test configuration manager:
```bash
python3 scripts/wiki_config_manager.py
```

Test wiki selector:
```bash
python3 scripts/wiki_selector.py
```

## Advanced Troubleshooting

### Using Environment Variables for Debugging
Set environment variables to enable additional debugging:

```bash
# Enable verbose curl output
export CURL_VERBOSE=1

# Increase Python logging level
export PYTHON_LOG_LEVEL=DEBUG

# Run the script with debugging enabled
python3 scripts/wiki_secure_submission.py --wiki archwiki "Test Page" "test.md" "Debug test"
```

### Manual API Testing
Test API calls manually with curl:

```bash
# Get login token
curl -c cookies.txt "https://wiki.archlinux.org/api.php" \
  -d "action=query" \
  -d "meta=tokens" \
  -d "type=login" \
  -d "format=json"

# Login (replace TOKEN and PASSWORD)
curl -b cookies.txt -c cookies.txt "https://wiki.archlinux.org/api.php" \
  --data-urlencode "action=login" \
  --data-urlencode "lgname=your_username" \
  --data-urlencode "lgpassword=your_password" \
  --data-urlencode "lgtoken=TOKEN" \
  -d "format=json"

# Get CSRF token
curl -b cookies.txt -c cookies.txt "https://wiki.archlinux.org/api.php" \
  -d "action=query" \
  -d "meta=tokens" \
  -d "type=csrf" \
  -d "format=json"
```

### Network Diagnostics
Use network tools to diagnose connectivity issues:

```bash
# Check DNS resolution
nslookup wiki.archlinux.org

# Test HTTPS connectivity
openssl s_client -connect wiki.archlinux.org:443

# Trace network path
traceroute wiki.archlinux.org

# Check for packet loss
ping wiki.archlinux.org
```

## Reporting Issues

If you encounter issues that you cannot resolve:

1. **Gather Information:**
   - Error message and stack trace
   - Log file content
   - Python version: `python3 --version`
   - Operating system information
   - Wiki you're trying to access
   - Steps to reproduce the issue

2. **Check Existing Issues:**
   - Search the project's GitHub issues
   - Check if the issue has already been reported

3. **Create a Detailed Report:**
   - Use a clear, descriptive title
   - Include all relevant information gathered
   - Provide steps to reproduce
   - Include any relevant configuration details

4. **Include Environment Information:**
   - Operating system and version
   - Python version
   - Tool version (if available)
   - Network environment (corporate, home, etc.)

## Performance Issues

### Slow Submission Times
**Possible Causes:**
- Network latency
- Wiki server performance
- Large content files
- Multiple validation checks

**Solutions:**
1. Check network performance
2. Try submitting during off-peak hours
3. Break large content into smaller submissions
4. Consider disabling some validation checks if not needed

### High Memory Usage
**Possible Causes:**
- Very large content files
- Multiple concurrent processes
- Memory leaks in dependencies

**Solutions:**
1. Process large files in smaller chunks
2. Limit concurrent submissions
3. Restart the script periodically for long-running processes
4. Update Python dependencies

## Security-Related Issues

### Suspicious Activity Alerts
**Possible Causes:**
- Unusual editing patterns
- Multiple rapid edits
- Content flagged by automated systems

**Solutions:**
1. Review edit frequency and patterns
2. Add delays between submissions
3. Use bot accounts where appropriate
4. Contact wiki administrators to explain automated editing

### Credential Security Concerns
**Possible Causes:**
- Shared accounts
- Weak passwords
- Credential exposure

**Solutions:**
1. Use unique, strong passwords
2. Enable two-factor authentication
3. Use application-specific passwords when available
4. Regularly rotate credentials
5. Monitor account activity

## Platform-Specific Issues

### Linux
**Common Issues:**
- File permission problems
- Missing dependencies
- SELinux/AppArmor restrictions

**Solutions:**
1. Check file permissions with `ls -l`
2. Install dependencies with package manager
3. Check SELinux/AppArmor logs for denials

### macOS
**Common Issues:**
- Python installation conflicts
- Homebrew vs system Python
- File system case sensitivity

**Solutions:**
1. Use consistent Python installation
2. Check file paths for case sensitivity
3. Update Homebrew packages if using Homebrew Python

### Windows
**Common Issues:**
- Line ending differences
- Path separator issues
- PowerShell vs Command Prompt differences

**Solutions:**
1. Use consistent line endings (LF)
2. Use forward slashes or raw strings for paths
3. Test in both PowerShell and Command Prompt

## Wiki-Specific Issues

### Wikimedia Projects (Wikipedia, Wiktionary, etc.)
**Common Issues:**
- Strict abuse filters
- Bot account requirements
- Edit throttling

**Solutions:**
1. Review Wikimedia's bot policies
2. Request bot approval if making many edits
3. Implement appropriate delays between edits

### Fandom Wikis
**Common Issues:**
- Custom spam filters
- Community-specific policies
- Varying API configurations

**Solutions:**
1. Review the specific wiki's policies
2. Contact wiki administrators for guidance
3. Test with sandbox pages first

### Private/Corporate Wikis
**Common Issues:**
- Custom authentication
- Firewall restrictions
- Internal DNS requirements

**Solutions:**
1. Verify network access to the wiki
2. Check authentication requirements
3. Ensure proper DNS resolution

## Getting Additional Help

### Community Resources
1. Project GitHub repository issues
2. Wiki community forums
3. Stack Overflow for technical questions
4. Reddit communities for specific wikis

### Professional Support
1. Wiki administrators
2. IT department (for corporate wikis)
3. Professional consulting services

### Documentation
1. This troubleshooting guide
2. Usage guide (`docs/usage_guide.md`)
3. API reference (`docs/api_reference.md`)
4. Security guide (`SECURITY_GUIDE.md`)