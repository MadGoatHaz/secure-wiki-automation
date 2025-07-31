#!/bin/bash

# Arch Wiki Submit Edit Script
# This script submits an edit to a page on the Arch Wiki

# Configuration
ARCH_WIKI_API="https://wiki.archlinux.org/api.php"
COOKIES_FILE="/tmp/archwiki_cookies.txt"
CSRF_TOKEN_FILE="/tmp/archwiki_csrf_token.txt"

# Check if required files exist
if [ ! -f "$COOKIES_FILE" ]; then
    echo "Error: Cookies file not found. Please login first."
    exit 1
fi

if [ ! -f "$CSRF_TOKEN_FILE" ]; then
    echo "Error: CSRF token file not found. Please get CSRF token first."
    exit 1
fi

# Read CSRF token
CSRF_TOKEN=$(cat "$CSRF_TOKEN_FILE")

# Check if title and content files are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <page_title> <content_file> [edit_summary]"
    exit 1
fi

PAGE_TITLE="$1"
CONTENT_FILE="$2"
EDIT_SUMMARY="$3"

# If no edit summary provided, use default
if [ -z "$EDIT_SUMMARY" ]; then
    EDIT_SUMMARY="Automated update for Bluetooth troubleshooting documentation"
fi

# Check if content file exists
if [ ! -f "$CONTENT_FILE" ]; then
    echo "Error: Content file not found: $CONTENT_FILE"
    exit 1
fi

# Read content
CONTENT=$(cat "$CONTENT_FILE")

# Submit edit
echo "Submitting edit to page: $PAGE_TITLE"
EDIT_RESPONSE=$(curl -s -X POST "$ARCH_WIKI_API" \
    -d "action=edit" \
    -d "title=$PAGE_TITLE" \
    -d "text=$CONTENT" \
    -d "summary=$EDIT_SUMMARY" \
    -d "token=$CSRF_TOKEN" \
    -d "format=json" \
    -b "$COOKIES_FILE" -c "$COOKIES_FILE")

# Check response
EDIT_RESULT=$(echo "$EDIT_RESPONSE" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ "$EDIT_RESULT" != "Success" ]; then
    echo "Error: Edit failed"
    echo "Response: $EDIT_RESPONSE"
    exit 1
fi

echo "Edit submitted successfully!"
echo "Response: $EDIT_RESPONSE"