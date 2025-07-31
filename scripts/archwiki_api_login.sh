#!/bin/bash

# Arch Wiki API Login Script
# This script handles authentication with the Arch Wiki API

# Configuration
ARCH_WIKI_API="https://wiki.archlinux.org/api.php"
COOKIES_FILE="/tmp/archwiki_cookies.txt"

# Check if credentials file exists
if [ ! -f "archwiki_credentials.conf" ]; then
    echo "Error: archwiki_credentials.conf not found"
    echo "Please create a file with your Arch Wiki credentials:"
    echo "USERNAME=your_username"
    echo "PASSWORD=your_password"
    exit 1
fi

# Load credentials
source archwiki_credentials.conf

# Get login token
echo "Getting login token..."
LOGIN_TOKEN_RESPONSE=$(curl -s -X POST "$ARCH_WIKI_API" \
    -d "action=query&meta=tokens&type=login&format=json" \
    -c "$COOKIES_FILE")

LOGIN_TOKEN=$(echo "$LOGIN_TOKEN_RESPONSE" | grep -o '"logintoken":"[^"]*"' | cut -d'"' -f4)

if [ -z "$LOGIN_TOKEN" ]; then
    echo "Error: Failed to get login token"
    echo "Response: $LOGIN_TOKEN_RESPONSE"
    exit 1
fi

echo "Login token obtained: $LOGIN_TOKEN"

# Perform login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$ARCH_WIKI_API" \
    -d "action=login&lgname=$USERNAME&lgpassword=$PASSWORD&lgtoken=$LOGIN_TOKEN&format=json" \
    -b "$COOKIES_FILE" -c "$COOKIES_FILE")

LOGIN_RESULT=$(echo "$LOGIN_RESPONSE" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ "$LOGIN_RESULT" != "Success" ]; then
    echo "Error: Login failed"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "Login successful!"