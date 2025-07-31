#!/bin/bash
#
# Script to retrieve wiki page content

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <wiki_api_url> <page_title>"
    echo "Example: $0 \"https://wiki.archlinux.org/api.php\" \"Realtek Bluetooth troubleshooting\""
    exit 1
fi

WIKI_API_URL="$1"
PAGE_TITLE="$2"

# Get page content
curl -s -X POST "$WIKI_API_URL" \
    -d "action=query" \
    -d "prop=extracts|info" \
    -d "titles=$PAGE_TITLE" \
    -d "format=json" \
    -d "explaintext=1" \
    --user-agent "WikiContentRetriever/1.0"