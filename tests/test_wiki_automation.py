#!/usr/bin/env python3
"""
Test suite for the Secure Wiki Automation Tool
"""

import unittest
import json
import os
import tempfile
import sys
from unittest.mock import patch, mock_open, MagicMock

# Add the scripts directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from wiki_config_manager import WikiConfigManager
from wiki_selector import WikiSelector
from wiki_validator import WikiValidator

class TestWikiConfigManager(unittest.TestCase):
    """Test cases for WikiConfigManager"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            "default_wiki": "archwiki",
            "wikis": {
                "archwiki": {
                    "name": "Arch Wiki",
                    "api_url": "https://wiki.archlinux.org/api.php",
                    "user_agent": "WikiSecureBot/1.0 (Arch Wiki)",
                    "validation_rules": {
                        "related_articles": "{{Related articles",
                        "subsection_format": "===",
                        "note_box": "{{Note|"
                    }
                }
            }
        }
        
        # Create temporary files for testing
        self.temp_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_config, self.temp_config_file)
        self.temp_config_file.close()
        
        self.temp_user_config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_user_config_file.close()
        
        self.config_manager = WikiConfigManager(
            config_file=self.temp_config_file.name,
            user_config_file=self.temp_user_config_file.name
        )
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        os.unlink(self.temp_config_file.name)
        os.unlink(self.temp_user_config_file.name)
    
    def test_load_config(self):
        """Test loading configuration from file."""
        config = self.config_manager.load_config()
        self.assertEqual(config, self.test_config)
    
    def test_load_user_config_empty(self):
        """Test loading user configuration when file is empty."""
        user_config = self.config_manager.load_user_config()
        self.assertEqual(user_config, {})
    
    def test_merge_configs(self):
        """Test merging main and user configurations."""
        merged_config = self.config_manager.merge_configs()
        self.assertEqual(merged_config, self.test_config)
    
    def test_get_wiki_config(self):
        """Test getting configuration for a specific wiki."""
        wiki_config = self.config_manager.get_wiki_config("archwiki")
        self.assertEqual(wiki_config, self.test_config["wikis"]["archwiki"])
    
    def test_get_wiki_config_not_found(self):
        """Test getting configuration for a non-existent wiki."""
        wiki_config = self.config_manager.get_wiki_config("nonexistent")
        self.assertIsNone(wiki_config)
    
    def test_get_wiki_list(self):
        """Test getting list of all wikis."""
        wiki_list = self.config_manager.get_wiki_list()
        self.assertEqual(wiki_list, self.test_config["wikis"])
    
    def test_get_default_wiki(self):
        """Test getting the default wiki."""
        default_wiki = self.config_manager.get_default_wiki()
        self.assertEqual(default_wiki, "archwiki")
    
    def test_validate_api_url_valid(self):
        """Test validating a valid API URL."""
        valid_url = "https://wiki.archlinux.org/api.php"
        self.assertTrue(self.config_manager.validate_api_url(valid_url))
    
    def test_validate_api_url_invalid_protocol(self):
        """Test validating an API URL with invalid protocol."""
        invalid_url = "http://wiki.archlinux.org/api.php"
        self.assertFalse(self.config_manager.validate_api_url(invalid_url))
    
    def test_validate_api_url_invalid_endpoint(self):
        """Test validating an API URL with invalid endpoint."""
        invalid_url = "https://wiki.archlinux.org/index.php"
        self.assertFalse(self.config_manager.validate_api_url(invalid_url))

class TestWikiSelector(unittest.TestCase):
    """Test cases for WikiSelector"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            "default_wiki": "archwiki",
            "wikis": {
                "archwiki": {
                    "name": "Arch Wiki",
                    "api_url": "https://wiki.archlinux.org/api.php",
                    "user_agent": "WikiSecureBot/1.0 (Arch Wiki)",
                    "validation_rules": {}
                },
                "wikipedia": {
                    "name": "Wikipedia",
                    "api_url": "https://en.wikipedia.org/api.php",
                    "user_agent": "WikiSecureBot/1.0 (Wikipedia)",
                    "validation_rules": {}
                }
            }
        }
        
        # Mock the config manager
        self.mock_config_manager = MagicMock()
        self.mock_config_manager.merge_configs.return_value = self.test_config
        self.mock_config_manager.get_wiki_list.return_value = self.test_config["wikis"]
        self.mock_config_manager.get_wiki_config.side_effect = lambda wiki_id: self.test_config["wikis"].get(wiki_id)
        self.mock_config_manager.validate_api_url.side_effect = lambda url: url.startswith("https://") and url.endswith("/api.php")
        
        self.wiki_selector = WikiSelector(self.mock_config_manager)
    
    def test_categorize_wikis(self):
        """Test categorizing wikis."""
        categorized = self.wiki_selector._categorize_wikis(self.test_config["wikis"])
        self.assertIn("Wikimedia Foundation", categorized)
        self.assertIn("Technology", categorized)
        self.assertIn("Other", categorized)
        self.assertIn("archwiki", categorized["Technology"])
        self.assertIn("wikipedia", categorized["Wikimedia Foundation"])

class TestWikiValidator(unittest.TestCase):
    """Test cases for WikiValidator"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.validator = WikiValidator()
    
    def test_check_wiki_specific_features(self):
        """Test checking wiki-specific features."""
        content = """
        == Introduction ==
        This is a test page.
        
        {{Related articles|Article1|Article2}}
        
        === Section 1 ===
        Content here.
        
        {{Note|This is an important note.}}
        """
        
        validation_rules = {
            "related_articles": "{{Related articles",
            "subsection_format": "===",
            "note_box": "{{Note|"
        }
        
        results = self.validator.check_wiki_specific_features(content, validation_rules)
        self.assertTrue(results["related_articles"])
        self.assertTrue(results["subsection_format"])
        self.assertTrue(results["note_box"])
    
    def test_check_wiki_specific_features_not_found(self):
        """Test checking wiki-specific features that are not found."""
        content = """
        == Introduction ==
        This is a test page.
        """
        
        validation_rules = {
            "infobox": "{{Infobox",
            "navbox": "{{Navbox"
        }
        
        results = self.validator.check_wiki_specific_features(content, validation_rules)
        self.assertFalse(results["infobox"])
        self.assertFalse(results["navbox"])

def main():
    """Run all tests."""
    unittest.main()

if __name__ == "__main__":
    main()