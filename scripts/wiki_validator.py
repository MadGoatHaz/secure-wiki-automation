#!/usr/bin/env python3
"""
Wiki Validator
Handles configurable validation for different wiki styles.
"""

import requests
import sys
from typing import Dict, Any, Optional, Tuple

class WikiValidator:
    def __init__(self):
        """Initialize the WikiValidator."""
        pass
    
    def fetch_wiki_page(self, wiki_api_url: str, page_title: str) -> Optional[str]:
        """
        Fetch the content of a page from a wiki.
        
        Args:
            wiki_api_url: The API URL of the wiki
            page_title: The title of the page to fetch
            
        Returns:
            The content of the page, or None if fetching failed
        """
        try:
            params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "revisions",
                "rvprop": "content"
            }
            
            response = requests.get(wiki_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return None
                
            # Get the first (and likely only) page
            page_id = list(pages.keys())[0]
            page = pages[page_id]
            
            if "missing" in page:
                return None
                
            revisions = page.get("revisions", [])
            if not revisions:
                return None
                
            # Get the latest revision content
            content = revisions[0].get("*")
            if content is None:
                return None
                
            return content
            
        except requests.RequestException as e:
            print(f"Error fetching page: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            return None
    
    def read_local_file(self, file_path: str) -> Optional[str]:
        """
        Read the content of a local file.
        
        Args:
            file_path: The path to the file to read
            
        Returns:
            The content of the file, or None if reading failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading local file: {e}", file=sys.stderr)
            return None
    
    def check_wiki_specific_features(self, content: str, validation_rules: Dict[str, str]) -> Dict[str, bool]:
        """
        Check if the content has wiki-specific features based on validation rules.
        
        Args:
            content: The content to check
            validation_rules: Dictionary of validation rules
            
        Returns:
            Dictionary with rule names as keys and boolean results as values
        """
        checks = {}
        for rule_name, pattern in validation_rules.items():
            # Special handling for no_duplicate_numbering rule
            if rule_name == "no_duplicate_numbering":
                checks[rule_name] = pattern not in content
            else:
                checks[rule_name] = pattern in content
        return checks
    
    def validate_submission(self, wiki_api_url: str, page_title: str, content_file: str, 
                          validation_rules: Dict[str, str]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate that the submitted content matches the local file and meets wiki-specific criteria.
        
        Args:
            wiki_api_url: The API URL of the wiki
            page_title: The title of the page that was submitted
            content_file: Path to the local content file
            validation_rules: Dictionary of wiki-specific validation rules
            
        Returns:
            Tuple containing (success, validation_details)
        """
        validation_details = {
            "content_match": False,
            "wiki_features": {},
            "local_features": {},
            "content_lengths": {
                "wiki": 0,
                "local": 0
            }
        }
        
        # Fetch content from wiki
        wiki_content = self.fetch_wiki_page(wiki_api_url, page_title)
        if wiki_content is None:
            return False, validation_details
            
        # Read local content
        local_content = self.read_local_file(content_file)
        if local_content is None:
            return False, validation_details
            
        # Store content lengths for comparison
        validation_details["content_lengths"]["wiki"] = len(wiki_content)
        validation_details["content_lengths"]["local"] = len(local_content)
        
        # Check wiki-specific features
        if validation_rules:
            validation_details["wiki_features"] = self.check_wiki_specific_features(wiki_content, validation_rules)
            validation_details["local_features"] = self.check_wiki_specific_features(local_content, validation_rules)
        
        # Compare content (simplified comparison)
        # Remove whitespace differences for comparison
        wiki_content_stripped = wiki_content.strip()
        local_content_stripped = local_content.strip()
        
        validation_details["content_match"] = wiki_content_stripped == local_content_stripped
        
        # Overall success is based on content matching
        success = validation_details["content_match"]
        
        return success, validation_details
    
    def print_validation_report(self, success: bool, validation_details: Dict[str, Any], 
                              wiki_name: str) -> None:
        """
        Print a detailed validation report.
        
        Args:
            success: Whether the validation was successful
            validation_details: Dictionary containing validation details
            wiki_name: Name of the wiki for context
        """
        print(f"\n\033[0;34m[VALIDATION]\033[0m Validation report for {wiki_name}:")
        
        # Content match result
        if validation_details["content_match"]:
            print("\033[0;32m✓\033[0m Content matches between local file and wiki page")
        else:
            print("\033[0;31m✗\033[0m Content differs between local file and wiki page")
            print(f"  Local content length: {validation_details['content_lengths']['local']} characters")
            print(f"  Wiki content length: {validation_details['content_lengths']['wiki']} characters")
        
        # Wiki-specific features
        wiki_features = validation_details.get("wiki_features", {})
        if wiki_features:
            print(f"\n\033[0;34m[VALIDATION]\033[0m Wiki-specific features check:")
            all_features_present = True
            for feature, present in wiki_features.items():
                status = "\033[0;32m✓\033[0m" if present else "\033[0;31m✗\033[0m"
                print(f"  {status} {feature}")
                if not present:
                    all_features_present = False
            
            if all_features_present:
                print("\033[0;32m✓\033[0m All wiki-specific features are present")
            else:
                print("\033[0;33m!\033[0m Some wiki-specific features are missing (not critical)")
        
        # Overall result
        if success:
            print(f"\n\033[0;32m[VALIDATION SUCCESS]\033[0m Validation successful for {wiki_name}!")
        else:
            print(f"\n\033[0;31m[VALIDATION FAILURE]\033[0m Validation failed for {wiki_name}!")

def main():
    """Main function for testing the WikiValidator."""
    # This is just a basic test
    validator = WikiValidator()
    print("WikiValidator module loaded successfully!")

if __name__ == "__main__":
    main()