#!/usr/bin/env python3
"""
Wiki Configuration Manager
Handles loading and managing wiki configurations from JSON files.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

class WikiConfigManager:
    def __init__(self, config_file: str = "wiki_config.json", user_config_file: str = "user_wikis.json"):
        """
        Initialize the WikiConfigManager.
        
        Args:
            config_file: Path to the main configuration file
            user_config_file: Path to the user configuration file
        """
        self.config_file = config_file
        self.user_config_file = user_config_file
        self.config = {}
        self.user_config = {}
        self.merged_config = {}
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load the main configuration file.
        
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is invalid JSON
        """
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            return self.config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{self.config_file}' not found.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in configuration file '{self.config_file}': {e.msg}", e.doc, e.pos)
    
    def load_user_config(self) -> Dict[str, Any]:
        """
        Load the user configuration file if it exists.
        
        Returns:
            Dictionary containing the user configuration data, or empty dict if file doesn't exist
        """
        if os.path.exists(self.user_config_file):
            try:
                with open(self.user_config_file, 'r') as f:
                    self.user_config = json.load(f)
                return self.user_config
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in user configuration file '{self.user_config_file}': {e.msg}", file=sys.stderr)
                return {}
        return {}
    
    def merge_configs(self) -> Dict[str, Any]:
        """
        Merge the main configuration with the user configuration.
        User configurations take precedence over main configurations.
        
        Returns:
            Dictionary containing the merged configuration data
        """
        # Load both configurations
        self.load_config()
        self.load_user_config()
        
        # Start with main config
        self.merged_config = self.config.copy()
        
        # Merge user wikis if they exist
        if "wikis" in self.user_config:
            if "wikis" not in self.merged_config:
                self.merged_config["wikis"] = {}
            self.merged_config["wikis"].update(self.user_config["wikis"])
        
        # Update default wiki if specified in user config
        if "default_wiki" in self.user_config:
            self.merged_config["default_wiki"] = self.user_config["default_wiki"]
            
        return self.merged_config
    
    def get_wiki_config(self, wiki_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific wiki.
        
        Args:
            wiki_id: The ID of the wiki to retrieve configuration for
            
        Returns:
            Dictionary containing the wiki configuration, or None if not found
        """
        if not self.merged_config:
            self.merge_configs()
            
        return self.merged_config.get("wikis", {}).get(wiki_id)
    
    def get_wiki_list(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a list of all available wikis.
        
        Returns:
            Dictionary of wiki configurations keyed by wiki ID
        """
        if not self.merged_config:
            self.merge_configs()
            
        return self.merged_config.get("wikis", {})
    
    def get_default_wiki(self) -> str:
        """
        Get the default wiki ID.
        
        Returns:
            The ID of the default wiki
        """
        if not self.merged_config:
            self.merge_configs()
            
        return self.merged_config.get("default_wiki", "")
    
    def add_wiki(self, wiki_id: str, wiki_config: Dict[str, Any]) -> None:
        """
        Add a new wiki to the user configuration.
        
        Args:
            wiki_id: The ID for the new wiki
            wiki_config: Dictionary containing the wiki configuration
        """
        # Load user config or create empty if it doesn't exist
        self.load_user_config()
        
        # Add or update wikis in user config
        if "wikis" not in self.user_config:
            self.user_config["wikis"] = {}
        self.user_config["wikis"][wiki_id] = wiki_config
        
        # Save the updated user config
        try:
            with open(self.user_config_file, 'w') as f:
                json.dump(self.user_config, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save user configuration: {e}")
    
    def validate_api_url(self, api_url: str) -> bool:
        """
        Validate that an API URL is properly formatted.
        
        Args:
            api_url: The API URL to validate
            
        Returns:
            True if the URL is valid, False otherwise
        """
        # Check that URL starts with https://
        if not api_url.startswith("https://"):
            return False
            
        # Check that URL ends with api.php
        if not api_url.endswith("/api.php"):
            return False
            
        return True

def main():
    """Main function for testing the WikiConfigManager."""
    config_manager = WikiConfigManager()
    
    try:
        # Load and merge configurations
        merged_config = config_manager.merge_configs()
        print("Configuration loaded successfully!")
        print(f"Default wiki: {merged_config.get('default_wiki', 'Not set')}")
        print(f"Number of wikis: {len(merged_config.get('wikis', {}))}")
        
        # List all wikis
        print("\nAvailable wikis:")
        for wiki_id, wiki_config in config_manager.get_wiki_list().items():
            print(f"  {wiki_id}: {wiki_config.get('name', 'Unnamed wiki')}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()