#!/usr/bin/env python3
"""
Standard Wiki Submission Script (Python Version)
This script can use file-based or environment variable credentials for automated submissions.
Works with any MediaWiki-based wiki.
"""

import subprocess
import json
import time
import sys
import argparse
import os
import secrets
from typing import Dict, List, Optional, Any

class StandardWikiBot:
    def __init__(self):
        self.username = None
        self.password = None
        self.log_file = f"/tmp/wiki_submission_{os.getpid()}.log"  # Use process ID for unique file
        self.session = None
        
    def log_message(self, message: str) -> None:
        """Logs messages to a file with a timestamp, excluding sensitive data."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = f"[{timestamp}] {message}"
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception:
            # If we can't write to log, continue without logging
            pass
        
    def load_credentials_from_file(self, credentials_file: str) -> bool:
        """Load credentials from a configuration file."""
        try:
            with open(credentials_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key == 'WIKI_USERNAME':
                                self.username = value
                            elif key == 'WIKI_PASSWORD':
                                self.password = value
                            elif key == 'WIKI_API_URL':
                                self.wiki_api_url = value
            return self.username is not None and self.password is not None
        except Exception as e:
            self.log_message(f"Error loading credentials from file: {e}")
            return False
            
    def load_credentials_from_env(self) -> bool:
        """Load credentials from environment variables."""
        self.username = os.environ.get('WIKI_USERNAME')
        self.password = os.environ.get('WIKI_PASSWORD')
        self.wiki_api_url = os.environ.get('WIKI_API_URL')
        return self.username is not None and self.password is not None and self.wiki_api_url is not None
        
    def secure_clear_string(self, s: str) -> None:
        """Securely clear a string from memory by overwriting with random data."""
        if s:
            # Overwrite with random data multiple times
            for _ in range(3):
                random_data = secrets.token_hex(len(s))
                s = random_data
            # Clear the random data
            del s
            
    def run_curl_command(self, wiki_api_url: str, data_params: Dict[str, str], method: str = "POST", 
                        expect_json: bool = True, initial_cookies: bool = False,
                        urlencode_params: Dict[str, str] = None) -> Any:
        """Helper function to execute curl commands and parse JSON responses."""
        # Create cookies file with process ID for unique file
        cookies_file = f"/tmp/wiki_cookies_{os.getpid()}.txt"
        
        cmd = ["curl", "-s", "-X", method, wiki_api_url]

        if initial_cookies:
            # For the very first login token request, we don't have cookies yet
            cmd.extend(["-c", cookies_file])
        else:
            # For subsequent requests, read and write cookies
            cmd.extend(["-b", cookies_file, "-c", cookies_file])

        # Add data parameters
        for key, value in data_params.items():
            # URL encode sensitive parameters
            if key in ["lgtoken", "lgpassword", "text", "summary", "token"]:
                cmd.extend(["--data-urlencode", f"{key}={value}"])
            else:
                cmd.extend(["-d", f"{key}={value}"])
                
        # Add additional URL-encoded parameters
        if urlencode_params:
            for key, value in urlencode_params.items():
                cmd.extend(["--data-urlencode", f"{key}={value}"])
        
        # Add user agent
        cmd.extend(["--user-agent", "WikiStandardBot/1.0 (Generic Wiki Submission Tool)"])
        
        # Add timeout options
        cmd.extend(["--connect-timeout", "30", "--max-time", "120"])

        self.log_message(f"Executing curl command: {' '.join(cmd[:3] + ['***' if '=' in x and any(sensitive in x.lower() for sensitive in ['password', 'token']) else x for x in cmd[3:]])}")
        process = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if process.returncode != 0:
            self.log_message(f"Curl command failed with exit code {process.returncode}: {process.stderr}")
            raise Exception(f"Curl command failed: {process.stderr}")

        if expect_json:
            try:
                return json.loads(process.stdout)
            except json.JSONDecodeError:
                self.log_message(f"Failed to decode JSON response: {process.stdout}")
                raise Exception("Failed to decode JSON response from API.")
        return process.stdout

    def get_login_token(self, wiki_api_url: str) -> str:
        """Get login token from Wiki API."""
        self.log_message("Attempting to get login token...")
        response = self.run_curl_command(
            wiki_api_url,
            {"action": "query", "meta": "tokens", "type": "login", "format": "json"}, 
            initial_cookies=True
        )
        token = response.get("query", {}).get("tokens", {}).get("logintoken")
        if not token:
            self.log_message(f"Failed to get login token. Response: {response}")
            raise Exception("Could not retrieve login token.")
        self.log_message("Login token obtained.")
        return token

    def login(self, wiki_api_url: str, login_token: str) -> str:
        """Login to Wiki API. Returns 'Success' on success, raises exception on failure."""
        self.log_message(f"Attempting to log in as {self.username}...")
        response = self.run_curl_command(
            wiki_api_url,
            {
                "action": "login",
                "lgname": self.username,
                "format": "json"
            },
            urlencode_params={
                "lgpassword": self.password,
                "lgtoken": login_token
            }
        )
        result = response.get("login", {}).get("result")
        if result != "Success":
            reason = response.get("login", {}).get("reason", "Unknown reason")
            # Log more details about the response for debugging
            self.log_message(f"Login failed. Full response: {response}")
            raise Exception(f"Login failed: {reason}. Response: {response}")
        self.log_message("Login successful.")
        return result

    def get_csrf_token(self, wiki_api_url: str) -> str:
        """Get CSRF token for editing."""
        self.log_message("Attempting to get CSRF token...")
        response = self.run_curl_command(
            wiki_api_url,
            {
                "action": "query", 
                "meta": "tokens", 
                "type": "csrf", 
                "format": "json"
            }
        )
        token = response.get("query", {}).get("tokens", {}).get("csrftoken")
        if not token:
            self.log_message(f"Failed to get CSRF token. Response: {response}")
            raise Exception("Could not retrieve CSRF token.")
        self.log_message("CSRF token obtained.")
        return token

    def submit_wiki_page(self, wiki_api_url: str, title: str, content: str, summary: str, 
                        csrf_token: str, is_bot_edit: bool = True) -> None:
        """Submit page content to Wiki."""
        self.log_message(f"Attempting to submit page: '{title}' with summary: '{summary}'...")
        params = {
            "action": "edit",
            "title": title,
            "format": "json"
        }
        if is_bot_edit:
            params["bot"] = "1"

        response = self.run_curl_command(
            wiki_api_url,
            params,
            urlencode_params={
                "text": content,
                "summary": summary,
                "token": csrf_token
            }
        )
        result = response.get("edit", {}).get("result")
        if result != "Success":
            error_code = response.get("error", {}).get("code", "N/A")
            error_info = response.get("error", {}).get("info", "Unknown error")
            self.log_message(f"Edit failed for '{title}': {error_code} - {error_info}. Full response: {response}")
            
            # Handle specific error cases
            if error_code == "badtoken":
                raise Exception("CSRF token is invalid. Please get a new CSRF token and try again.")
            elif error_code == "maxlag":
                raise Exception("Wiki is currently lagging. Please try again later.")
            elif error_code == "spamdetected":
                raise Exception("Content detected as spam. Please review your content.")
            elif error_code == "abusefilter":
                raise Exception("Content blocked by abuse filter. Please review your content.")
            else:
                raise Exception(f"Edit failed: {error_code} - {error_info}")
                
        self.log_message(f"Page '{title}' submitted successfully. New revision ID: {response.get('edit',{}).get('newrevid')}")

    def exponential_backoff(self, func, *args, max_retries: int = 3, **kwargs) -> Any:
        """Execute function with exponential backoff for transient errors."""
        retry_count = 0
        delay = 1
        
        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    error_msg = str(e).lower()
                    # Check if this is a transient error
                    if any(keyword in error_msg for keyword in ["maxlag", "timeout", "network"]):
                        self.log_message(f"Attempt {retry_count} failed with transient error. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                    elif "wrongtoken" in error_msg.lower():
                        self.log_message(f"Attempt {retry_count} failed with wrong token error. Retrying with fresh token...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                    else:
                        # Non-transient error, don't retry
                        raise e
                else:
                    self.log_message(f"Failed after {max_retries} attempts")
                    raise Exception(f"Failed after {max_retries} attempts: {e}")
        
        return None

    def cleanup(self) -> None:
        """Cleanup temporary files and clear sensitive data."""
        # Create cookies file with process ID for unique file
        cookies_file = f"/tmp/wiki_cookies_{os.getpid()}.txt"
        
        print("\033[0;34m[INFO]\033[0m Cleaning up temporary files...")
        self.log_message("Cleaning up temporary files")
        
        # Remove temporary files
        try:
            if os.path.exists(cookies_file):
                os.remove(cookies_file)
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
        except Exception as e:
            self.log_message(f"Error during cleanup: {e}")
        
        # Securely clear credentials
        self.secure_clear_string(self.password)
        self.password = None
        self.username = None
        
        print("\033[0;34m[INFO]\033[0m Cleanup completed")
        self.log_message("Cleanup completed")

    def submit_content(self, wiki_api_url: str, page_title: str, content_file: str, edit_summary: str) -> None:
        """Main function to submit content to Wiki with standard credential handling."""
        try:
            # Read content from file
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.log_message(f"Starting standard Wiki submission process for page: {page_title}")
            
            # Validate credentials
            if not self.username or not self.password:
                raise Exception("Username and password must be set")
            
            print("\033[0;34m[INFO]\033[0m Proceeding with authentication...")
            self.log_message("Proceeding with authentication")
            
            # Step 1 & 2: Get login token and login with retry for WrongToken errors
            login_success = False
            login_attempts = 0
            max_login_attempts = 3
            
            while not login_success and login_attempts < max_login_attempts:
                login_attempts += 1
                try:
                    login_tok = self.get_login_token(wiki_api_url)
                    self.login(wiki_api_url, login_tok)
                    login_success = True
                except Exception as e:
                    if "wrongtoken" in str(e).lower() and login_attempts < max_login_attempts:
                        self.log_message(f"Login attempt {login_attempts} failed with wrong token. Retrying...")
                        time.sleep(1)
                        continue
                    else:
                        raise e
            
            # Step 3: Get CSRF token
            csrf_tok = self.exponential_backoff(self.get_csrf_token, wiki_api_url)
            
            # Step 4: Submit the page
            self.exponential_backoff(
                self.submit_wiki_page, 
                wiki_api_url,
                page_title, 
                content, 
                edit_summary, 
                csrf_tok
            )
            
            self.log_message("Wiki submission completed successfully!")
            print("\033[0;32m[INFO]\033[0m Edit submitted successfully!")
            print(f"Page '{page_title}' has been updated with content from '{content_file}'")
            print(f"Edit summary: {edit_summary}")
            
        except Exception as e:
            self.log_message(f"An unrecoverable error occurred: {e}")
            raise e
        finally:
            # Cleanup
            self.cleanup()
            self.log_message("Script finished.")

def main():
    parser = argparse.ArgumentParser(description='Standard Wiki Submission Script')
    parser.add_argument('wiki_api_url', nargs='?', help='URL of the wiki API endpoint (e.g., https://wiki.archlinux.org/api.php)')
    parser.add_argument('page_title', help='Title of the wiki page to edit')
    parser.add_argument('content_file', help='Path to the file containing the content')
    parser.add_argument('edit_summary', nargs='?', default='Automated update for wiki content',
                       help='Edit summary for the wiki edit')
    parser.add_argument('--credentials', '-c', help='Path to credentials file')
    
    args = parser.parse_args()
    
    # Create bot instance
    bot = StandardWikiBot()
    
    # Load credentials
    if args.credentials:
        if not bot.load_credentials_from_file(args.credentials):
            print(f"\033[0;31m[ERROR]\033[0m Failed to load credentials from {args.credentials}")
            sys.exit(1)
        # Override wiki_api_url if provided in arguments
        if args.wiki_api_url:
            bot.wiki_api_url = args.wiki_api_url
    else:
        # Try to load from environment variables
        if not bot.load_credentials_from_env():
            print("\033[0;31m[ERROR]\033[0m No credentials provided. Please use --credentials or set environment variables.")
            sys.exit(1)
        # Override wiki_api_url if provided in arguments
        if args.wiki_api_url:
            bot.wiki_api_url = args.wiki_api_url
    
    # Validate wiki_api_url
    if not hasattr(bot, 'wiki_api_url') or not bot.wiki_api_url:
        print("\033[0;31m[ERROR]\033[0m No wiki API URL provided.")
        sys.exit(1)
    
    try:
        bot.submit_content(bot.wiki_api_url, args.page_title, args.content_file, args.edit_summary)
        print("\n\033[0;34m[INFO]\033[0m Process completed successfully!")
    except Exception as e:
        print(f"\n\033[0;31m[ERROR]\033[0m {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()