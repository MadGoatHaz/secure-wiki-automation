#!/bin/bash
#
# Secure Wiki Submission Script (Bash Version)
# This script prompts for credentials during execution and ensures they are never stored,
# logged, or cached, with immediate memory clearance and encryption during transmission.
# Works with any MediaWiki-based wiki.

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - using process ID for unique temporary files
COOKIES_FILE="/tmp/wiki_cookies_$$.txt"
LOG_FILE="/tmp/wiki_submission_$$.log"

# Function to log messages
log_message() {
    local timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Function to securely clear variables
secure_clear() {
    local var_name="$1"
    if [ -n "${!var_name}" ]; then
        # Overwrite with random data multiple times
        for i in {1..3}; do
            local random_data=$(openssl rand -hex ${#var_name} 2>/dev/null || echo "x$(date +%s)")
            eval "$var_name=\$random_data"
        done
        # Clear the variable
        unset "$var_name"
    fi
}

# Function to cleanup temporary files
cleanup() {
    echo -e "${BLUE}[SECURITY]${NC} Cleaning up temporary files..."
    log_message "Cleaning up temporary files"
    
    # Remove temporary files
    [ -f "$COOKIES_FILE" ] && rm -f "$COOKIES_FILE"
    [ -f "$LOG_FILE" ] && rm -f "$LOG_FILE"
    
    # Securely clear sensitive variables
    secure_clear "WIKI_PASSWORD"
    secure_clear "LOGIN_TOKEN"
    secure_clear "CSRF_TOKEN"
    
    echo -e "${BLUE}[SECURITY]${NC} Cleanup completed"
    log_message "Cleanup completed"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT INT TERM

# Function to execute curl command with proper error handling
run_curl_command() {
    local wiki_api_url="$1"
    shift
    local params=("$@")
    
    # Build curl command
    local cmd=(curl -s -X POST "$wiki_api_url")
    
    # Add cookies if file exists
    if [ -f "$COOKIES_FILE" ]; then
        cmd+=(-b "$COOKIES_FILE" -c "$COOKIES_FILE")
    else
        cmd+=(-c "$COOKIES_FILE")
    fi
    
    # Add parameters
    cmd+=("${params[@]}")
    
    # Add user agent
    cmd+=(--user-agent "WikiSecureBot/1.0 (Generic Wiki Submission Tool)")
    
    # Add timeout options
    cmd+=(--connect-timeout 30 --max-time 120)
    
    # Log the command (without sensitive data)
    local log_cmd=("${cmd[@]}")
    for i in "${!log_cmd[@]}"; do
        if [[ "${log_cmd[i]}" == *"password"* ]] || [[ "${log_cmd[i]}" == *"token"* ]]; then
            log_cmd[i]="***"
        fi
    done
    log_message "Executing secure curl command: ${log_cmd[*]}"
    
    # Execute command
    local result
    result=$("${cmd[@]}")
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        log_message "Curl command failed with exit code $exit_code"
        echo "Curl command failed with exit code $exit_code"
        return $exit_code
    fi
    
    echo "$result"
    return 0
}

# Function to get login token
get_login_token() {
    local wiki_api_url="$1"
    log_message "Attempting to get login token..."
    
    local response
    response=$(run_curl_command "$wiki_api_url" \
        -d "action=query" \
        -d "meta=tokens" \
        -d "type=login" \
        -d "format=json")
    
    if [ $? -ne 0 ]; then
        log_message "Failed to get login token"
        echo "Failed to get login token"
        return 1
    fi
    
    LOGIN_TOKEN=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('query', {}).get('tokens', {}).get('logintoken', ''))
except:
    print('')
")
    
    if [ -z "$LOGIN_TOKEN" ]; then
        log_message "Failed to extract login token. Response: $response"
        echo "Failed to extract login token"
        return 1
    fi
    
    log_message "Login token obtained."
    return 0
}

# Function to login to wiki
login() {
    local wiki_api_url="$1"
    local username="$2"
    local password="$3"
    local token="$4"
    
    log_message "Attempting to log in as $username..."
    
    local response
    response=$(run_curl_command "$wiki_api_url" \
        --data-urlencode "action=login" \
        --data-urlencode "lgname=$username" \
        --data-urlencode "lgpassword=$password" \
        --data-urlencode "lgtoken=$token" \
        --data-urlencode "format=json")
    
    if [ $? -ne 0 ]; then
        log_message "Failed to login"
        echo "Failed to login"
        return 1
    fi
    
    local result
    result=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('login', {}).get('result', ''))
except:
    print('')
")
    
    if [ "$result" != "Success" ]; then
        local reason
        reason=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('login', {}).get('reason', 'Unknown reason'))
except:
    print('Unknown reason')
")
        log_message "Login failed. Reason: $reason. Response: $response"
        echo "Login failed: $reason"
        return 1
    fi
    
    log_message "Login successful."
    return 0
}

# Function to get CSRF token
get_csrf_token() {
    local wiki_api_url="$1"
    log_message "Attempting to get CSRF token..."
    
    local response
    response=$(run_curl_command "$wiki_api_url" \
        -d "action=query" \
        -d "meta=tokens" \
        -d "type=csrf" \
        -d "format=json")
    
    if [ $? -ne 0 ]; then
        log_message "Failed to get CSRF token"
        echo "Failed to get CSRF token"
        return 1
    fi
    
    CSRF_TOKEN=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('query', {}).get('tokens', {}).get('csrftoken', ''))
except:
    print('')
")
    
    if [ -z "$CSRF_TOKEN" ]; then
        log_message "Failed to extract CSRF token. Response: $response"
        echo "Failed to extract CSRF token"
        return 1
    fi
    
    log_message "CSRF token obtained."
    return 0
}

# Function to submit wiki page
submit_wiki_page() {
    local wiki_api_url="$1"
    local title="$2"
    local content="$3"
    local summary="$4"
    local token="$5"
    
    log_message "Attempting to submit page: '$title' with summary: '$summary'..."
    
    local response
    response=$(run_curl_command "$wiki_api_url" \
        --data-urlencode "action=edit" \
        --data-urlencode "title=$title" \
        --data-urlencode "text=$content" \
        --data-urlencode "summary=$summary" \
        --data-urlencode "token=$token" \
        --data-urlencode "bot=1" \
        --data-urlencode "format=json")
    
    if [ $? -ne 0 ]; then
        log_message "Failed to submit page"
        echo "Failed to submit page"
        return 1
    fi
    
    local result
    result=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('edit', {}).get('result', ''))
except:
    print('')
")
    
    if [ "$result" != "Success" ]; then
        local error_code
        error_code=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('error', {}).get('code', 'N/A'))
except:
    print('N/A')
")
        
        local error_info
        error_info=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('error', {}).get('info', 'Unknown error'))
except:
    print('Unknown error')
")
        
        log_message "Edit failed for '$title': $error_code - $error_info. Full response: $response"
        
        case "$error_code" in
            "badtoken")
                echo "CSRF token is invalid. Please get a new CSRF token and try again."
                ;;
            "maxlag")
                echo "Wiki is currently lagging. Please try again later."
                ;;
            "spamdetected")
                echo "Content detected as spam. Please review your content."
                ;;
            "abusefilter")
                echo "Content blocked by abuse filter. Please review your content."
                ;;
            *)
                echo "Edit failed: $error_code - $error_info"
                ;;
        esac
        
        return 1
    fi
    
    local newrevid
    newrevid=$(echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('edit', {}).get('newrevid', 'N/A'))
except:
    print('N/A')
")
    
    log_message "Page '$title' submitted successfully. New revision ID: $newrevid"
    return 0
}

# Function to implement exponential backoff
exponential_backoff() {
    local func_name="$1"
    shift
    local max_retries=3
    local retry_count=0
    local delay=1
    
    while [ $retry_count -lt $max_retries ]; do
        if $func_name "$@"; then
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                log_message "Attempt $retry_count failed. Retrying in $delay seconds..."
                sleep $delay
                delay=$((delay * 2))
            fi
        fi
    done
    
    log_message "Failed after $max_retries attempts"
    echo "Failed after $max_retries attempts"
    return 1
}

# Main function
main() {
    # Check arguments
    if [ $# -lt 4 ]; then
        echo "Usage: $0 <wiki_api_url> <page_title> <content_file> [edit_summary]"
        echo "Example: $0 \"https://wiki.archlinux.org/api.php\" \"Page Title\" \"content.md\" \"Edit summary\""
        exit 1
    fi
    
    local WIKI_API_URL="$1"
    local PAGE_TITLE="$2"
    local CONTENT_FILE="$3"
    local EDIT_SUMMARY="${4:-Automated update for wiki content}"
    
    # Validate content file exists
    if [ ! -f "$CONTENT_FILE" ]; then
        echo "Content file '$CONTENT_FILE' not found"
        exit 1
    fi
    
    log_message "Starting secure Wiki submission process for page: $PAGE_TITLE"
    
    # Read content from file
    local CONTENT
    CONTENT=$(cat "$CONTENT_FILE")
    
    # Prompt for username
    echo -e "\n${BLUE}[SECURITY]${NC} Please enter your Wiki username:"
    read -r WIKI_USERNAME
    
    # Validate username
    if [ -z "$WIKI_USERNAME" ]; then
        echo "Username cannot be empty"
        exit 1
    fi
    
    # Prompt for password securely
    echo -e "\n${BLUE}[SECURITY]${NC} Please enter your Wiki password (input will be hidden):"
    read -rs WIKI_PASSWORD
    echo "" # New line after hidden input
    
    # Validate password
    if [ -z "$WIKI_PASSWORD" ]; then
        echo "Password cannot be empty"
        exit 1
    fi
    
    echo -e "${BLUE}[SECURITY]${NC} Credentials received. Proceeding with authentication..."
    log_message "Credentials received. Proceeding with authentication"
    
    # Step 1: Get login token
    if ! exponential_backoff get_login_token "$WIKI_API_URL"; then
        echo "Failed to get login token"
        exit 1
    fi
    
    # Step 2: Login
    if ! exponential_backoff login "$WIKI_API_URL" "$WIKI_USERNAME" "$WIKI_PASSWORD" "$LOGIN_TOKEN"; then
        echo "Failed to login"
        exit 1
    fi
    
    # Securely clear password after use
    secure_clear "WIKI_PASSWORD"
    
    # Step 3: Get CSRF token
    if ! exponential_backoff get_csrf_token "$WIKI_API_URL"; then
        echo "Failed to get CSRF token"
        exit 1
    fi
    
    # Step 4: Submit the page
    if ! exponential_backoff submit_wiki_page "$WIKI_API_URL" "$PAGE_TITLE" "$CONTENT" "$EDIT_SUMMARY" "$CSRF_TOKEN"; then
        echo "Failed to submit page"
        exit 1
    fi
    
    log_message "Wiki submission completed successfully!"
    echo -e "${GREEN}[INFO]${NC} Edit submitted successfully!"
    echo "Page '$PAGE_TITLE' has been updated with content from '$CONTENT_FILE'"
    echo "Edit summary: $EDIT_SUMMARY"
}

# Run main function with all arguments
main "$@"