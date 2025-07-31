#!/bin/bash

# Arch Wiki Get CSRF Token Script
# This script retrieves the CSRF token needed for editing pages

# Configuration
ARCH_WIKI_API="https://wiki.archlinux.org/api.php"
COOKIES_FILE="/tmp/archwiki_cookies.txt"

# Check if cookies file exists
if [ ! -f "$COOKIES_FILE" ]; then
    echo "Error: Cookies file not found. Please login first."
    exit 1
fi

# Get CSRF token
echo "Getting CSRF token..."
CSRF_TOKEN_RESPONSE=$(curl -s -X POST "$ARCH_WIKI_API" \
    -d "action=query&meta=tokens&type=csrf&format=json" \
    -b "$COOKIES_FILE" -c "$COOKIES_FILE")

CSRF_TOKEN=$(echo "$CSRF_TOKEN_RESPONSE" | grep -o '"csrftoken":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CSRF_TOKEN" ]; then
    echo "Error: Failed to get CSRF token"
    echo "Response: $CSRF_TOKEN_RESPONSE"
    exit 1
fi

echo "CSRF token obtained: $CSRF_TOKEN"
echo "$CSRF_TOKEN" > /tmp/archwiki_csrf_token.txt