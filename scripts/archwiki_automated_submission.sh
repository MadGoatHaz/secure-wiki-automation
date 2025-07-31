#!/bin/bash

# Arch Wiki Automated Submission Script
# This script orchestrates the entire process of submitting content to Arch Wiki

# Configuration
ARCH_WIKI_API="https://wiki.archlinux.org/api.php"
COOKIES_FILE="/tmp/archwiki_cookies.txt"
CSRF_TOKEN_FILE="/tmp/archwiki_csrf_token.txt"
CREDENTIALS_FILE="archwiki_credentials.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if credentials file exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    print_error "Credentials file not found: $CREDENTIALS_FILE"
    echo "Please create a file named 'archwiki_credentials.conf' with your credentials:"
    echo "USERNAME=your_username"
    echo "PASSWORD=your_password"
    exit 1
fi

# Load credentials
source "$CREDENTIALS_FILE"

# Check if required parameters are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <page_title> <content_file> [edit_summary]"
    echo "Example: $0 \"Bluetooth\" \"archwiki_submission_content.md\" \"Add troubleshooting section for Realtek Bluetooth authentication failures\""
    exit 1
fi

PAGE_TITLE="$1"
CONTENT_FILE="$2"
EDIT_SUMMARY="$3"

# If no edit summary provided, use default
if [ -z "$EDIT_SUMMARY" ]; then
    EDIT_SUMMARY="Add troubleshooting section for Realtek Bluetooth authentication failures"
fi

print_status "Starting Arch Wiki automated submission process..."

# Step 1: Login
print_status "Step 1: Logging in to Arch Wiki..."
if ! ./scripts/archwiki_api_login.sh; then
    print_error "Login failed"
    exit 1
fi

# Step 2: Get CSRF token
print_status "Step 2: Getting CSRF token..."
if ! ./scripts/archwiki_get_csrf_token.sh; then
    print_error "Failed to get CSRF token"
    exit 1
fi

# Step 3: Submit edit
print_status "Step 3: Submitting edit to page: $PAGE_TITLE"
if ! ./scripts/archwiki_submit_edit.sh "$PAGE_TITLE" "$CONTENT_FILE" "$EDIT_SUMMARY"; then
    print_error "Edit submission failed"
    exit 1
fi

print_status "Arch Wiki submission completed successfully!"
echo "Page '$PAGE_TITLE' has been updated with content from '$CONTENT_FILE'"
echo "Edit summary: $EDIT_SUMMARY"

# Cleanup temporary files
print_status "Cleaning up temporary files..."
rm -f "$COOKIES_FILE" "$CSRF_TOKEN_FILE"

print_status "Process completed!"