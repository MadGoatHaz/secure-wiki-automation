#!/usr/bin/env python3
"""
Wiki Selector
Handles wiki selection and registration for the Secure Wiki Automation Tool.
"""

import sys
import re
from typing import Dict, Any, Optional, Tuple
from wiki_config_manager import WikiConfigManager

class WikiSelector:
    def __init__(self, config_manager: WikiConfigManager):
        """
        Initialize the WikiSelector.
        
        Args:
            config_manager: An instance of WikiConfigManager
        """
        self.config_manager = config_manager
        self.merged_config = {}
        
    def select_wiki_interactive(self) -> Tuple[str, Dict[str, Any]]:
        """
        Interactively select a wiki from the available options.
        
        Returns:
            Tuple containing (wiki_id, wiki_config)
        """
        # Load configurations
        self.merged_config = self.config_manager.merge_configs()
        wiki_list = self.config_manager.get_wiki_list()
        
        if not wiki_list:
            raise Exception("No wikis available in configuration.")
        
        # Group wikis by category for better presentation
        categorized_wikis = self._categorize_wikis(wiki_list)
        
        # Display categorized wiki list
        print("\nSelect a wiki:")
        option_number = 1
        option_map = {}
        
        # Display Wikimedia Foundation wikis first
        if "Wikimedia Foundation" in categorized_wikis:
            print("\nWikimedia Foundation Wikis:")
            for wiki_id in categorized_wikis["Wikimedia Foundation"]:
                wiki_config = wiki_list[wiki_id]
                print(f"{option_number}. {wiki_config['name']} ({wiki_config['api_url']})")
                option_map[str(option_number)] = wiki_id
                option_number += 1
        
        # Display Technology wikis
        if "Technology" in categorized_wikis:
            print("\nTechnology Wikis:")
            for wiki_id in categorized_wikis["Technology"]:
                wiki_config = wiki_list[wiki_id]
                print(f"{option_number}. {wiki_config['name']} ({wiki_config['api_url']})")
                option_map[str(option_number)] = wiki_id
                option_number += 1
        
        # Display Fandom wikis
        if "Fandom" in categorized_wikis:
            print("\nFandom Wikis:")
            for wiki_id in categorized_wikis["Fandom"]:
                wiki_config = wiki_list[wiki_id]
                print(f"{option_number}. {wiki_config['name']} ({wiki_config['api_url']})")
                option_map[str(option_number)] = wiki_id
                option_number += 1
        
        # Display Other wikis
        if "Other" in categorized_wikis:
            print("\nOther Wikis:")
            for wiki_id in categorized_wikis["Other"]:
                wiki_config = wiki_list[wiki_id]
                print(f"{option_number}. {wiki_config['name']} ({wiki_config['api_url']})")
                option_map[str(option_number)] = wiki_id
                option_number += 1
        
        # Add custom options
        print(f"\n{option_number}. Custom Wiki URL")
        option_map[str(option_number)] = "custom_url"
        option_number += 1
        
        print(f"{option_number}. Add New Wiki")
        option_map[str(option_number)] = "add_wiki"
        
        # Get user choice
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{option_number}): ").strip()
                if choice in option_map:
                    selected_wiki_id = option_map[choice]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)
        
        # Handle special options
        if selected_wiki_id == "custom_url":
            return self._handle_custom_url()
        elif selected_wiki_id == "add_wiki":
            return self._handle_add_wiki()
        else:
            # Return selected wiki
            wiki_config = self.config_manager.get_wiki_config(selected_wiki_id)
            if wiki_config:
                return selected_wiki_id, wiki_config
            else:
                raise Exception(f"Wiki configuration for '{selected_wiki_id}' not found.")
    
    def _categorize_wikis(self, wiki_list: Dict[str, Dict[str, Any]]) -> Dict[str, list]:
        """
        Categorize wikis for better presentation.
        
        Args:
            wiki_list: Dictionary of wiki configurations
            
        Returns:
            Dictionary with categories as keys and lists of wiki IDs as values
        """
        categories = {
            "Wikimedia Foundation": [],
            "Technology": [],
            "Fandom": [],
            "Other": []
        }
        
        for wiki_id, wiki_config in wiki_list.items():
            wiki_name = wiki_config.get("name", "").lower()
            
            # Wikimedia Foundation wikis
            if any(name in wiki_name for name in ["wikipedia", "wiktionary", "wikibooks", 
                                                  "wikiquote", "wikisource", "wikiversity", 
                                                  "wikidata", "wikimedia commons"]):
                categories["Wikimedia Foundation"].append(wiki_id)
            
            # Technology wikis
            elif any(name in wiki_name for name in ["arch wiki", "ubuntu wiki", "debian wiki", 
                                                    "gentoo wiki", "fedora wiki", "python wiki"]):
                categories["Technology"].append(wiki_id)
            
            # Fandom wikis
            elif "fandom" in wiki_name:
                categories["Fandom"].append(wiki_id)
            
            # Other wikis
            else:
                categories["Other"].append(wiki_id)
        
        return categories
    
    def _handle_custom_url(self) -> Tuple[str, Dict[str, Any]]:
        """
        Handle custom wiki URL input.
        
        Returns:
            Tuple containing (wiki_id, wiki_config) for custom URL
        """
        while True:
            try:
                api_url = input("Enter the wiki API URL (e.g., https://wiki.example.com/api.php): ").strip()
                if self.config_manager.validate_api_url(api_url):
                    # Extract domain name for wiki ID
                    domain_match = re.search(r"https://([^/]+)", api_url)
                    if domain_match:
                        wiki_id = domain_match.group(1).replace(".", "_").replace("-", "_")
                    else:
                        wiki_id = "custom_wiki"
                    
                    wiki_config = {
                        "name": f"Custom Wiki ({api_url})",
                        "api_url": api_url,
                        "user_agent": "WikiSecureBot/1.0 (Custom Wiki)",
                        "validation_rules": {}
                    }
                    return wiki_id, wiki_config
                else:
                    print("Invalid API URL. Please ensure it starts with 'https://' and ends with '/api.php'")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)
    
    def _handle_add_wiki(self) -> Tuple[str, Dict[str, Any]]:
        """
        Handle adding a new wiki interactively.
        
        Returns:
            Tuple containing (wiki_id, wiki_config) for the new wiki
        """
        print("\nAdd New Wiki")
        print("-------------")
        
        # Get wiki ID
        while True:
            try:
                wiki_id = input("Enter a unique ID for this wiki (e.g., my_wiki): ").strip()
                if wiki_id and re.match(r"^[a-zA-Z0-9_]+$", wiki_id):
                    # Check if wiki ID already exists
                    if self.config_manager.get_wiki_config(wiki_id):
                        print(f"Wiki ID '{wiki_id}' already exists. Please choose a different ID.")
                        continue
                    break
                else:
                    print("Invalid wiki ID. Use only letters, numbers, and underscores.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)
        
        # Get wiki name
        while True:
            try:
                wiki_name = input("Enter the wiki name: ").strip()
                if wiki_name:
                    break
                else:
                    print("Wiki name cannot be empty.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)
        
        # Get API URL
        while True:
            try:
                api_url = input("Enter the wiki API URL (e.g., https://wiki.example.com/api.php): ").strip()
                if self.config_manager.validate_api_url(api_url):
                    break
                else:
                    print("Invalid API URL. Please ensure it starts with 'https://' and ends with '/api.php'")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                sys.exit(0)
        
        # Get user agent (optional)
        try:
            user_agent = input("Enter user agent string (optional, press Enter for default): ").strip()
            if not user_agent:
                user_agent = f"WikiSecureBot/1.0 ({wiki_name})"
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)
        
        # Create wiki configuration
        wiki_config = {
            "name": wiki_name,
            "api_url": api_url,
            "user_agent": user_agent,
            "validation_rules": {}
        }
        
        # Add to user configuration
        try:
            self.config_manager.add_wiki(wiki_id, wiki_config)
            print(f"\nWiki '{wiki_name}' added successfully!")
        except Exception as e:
            print(f"Warning: Failed to save wiki to user configuration: {e}")
            print("The wiki will be available for this session only.")
        
        return wiki_id, wiki_config

def main():
    """Main function for testing the WikiSelector."""
    config_manager = WikiConfigManager()
    wiki_selector = WikiSelector(config_manager)
    
    try:
        wiki_id, wiki_config = wiki_selector.select_wiki_interactive()
        print(f"\nSelected wiki: {wiki_config['name']}")
        print(f"API URL: {wiki_config['api_url']}")
        print(f"User agent: {wiki_config['user_agent']}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()