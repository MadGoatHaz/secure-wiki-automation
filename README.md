# Secure Wiki Automation Tool

A enhanced, generic solution for programmatically submitting content to any MediaWiki-based wiki with secure credential handling, configurable validation, and an intuitive wiki selection interface.

## Features

### Multi-Wiki Support
- **Predefined Wikis**: Comes with configurations for 20+ popular MediaWiki-based wikis
  - Wikimedia Foundation wikis (Wikipedia, Wiktionary, etc.)
  - Technology wikis (Arch Wiki, Ubuntu Wiki, etc.)
  - Fandom wikis (Minecraft, League of Legends, etc.)
- **Custom Wikis**: Easily add your own wiki configurations
- **Generic Compatibility**: Works with any MediaWiki-based wiki

### Secure Credential Handling
- **Runtime Entry**: Credentials prompted during execution, never stored
- **Hidden Input**: Password input is hidden to prevent shoulder surfing
- **Memory Security**: Immediate clearing of credentials from memory
- **No Logging**: Credentials never logged or cached

### Configurable Validation System
- **Wiki-Specific Rules**: Different validation rules for different wiki types
- **Content Matching**: Verifies uploaded content matches local file
- **Enhanced Features**: Checks for wiki-specific formatting elements
- **Detailed Reporting**: Color-coded success/failure indicators

### Intuitive Wiki Selection
- **Interactive Menu**: Easy selection from predefined wikis
- **Direct Selection**: Command-line wiki selection by name
- **Custom URLs**: Support for custom wiki API endpoints
- **Wiki Registration**: Interactive addition of new wikis

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/secure-wiki-automation.git
   cd secure-wiki-automation
   ```

2. Ensure you have Python 3 installed:
   ```bash
   python3 --version
   ```

3. Install required dependencies:
   ```bash
   pip install requests
   ```

## Usage

### Basic Usage

```bash
# Interactive wiki selection
python3 scripts/wiki_secure_submission.py --select-wiki "Page Title" "content_file.md" "Edit summary"

# Direct wiki selection by ID
python3 scripts/wiki_secure_submission.py --wiki archwiki "Page Title" "content_file.md" "Edit summary"

# Custom wiki URL
python3 scripts/wiki_secure_submission.py --api-url "https://mywiki.example.com/api.php" "Page Title" "content_file.md" "Edit summary"

# Add new wiki interactively
python3 scripts/wiki_secure_submission.py --add-wiki "Page Title" "content_file.md" "Edit summary"
```

### Command-Line Arguments

- `page_title`: Title of the wiki page to edit
- `content_file`: Path to the file containing the content
- `edit_summary`: Edit summary for the wiki edit (optional, defaults to "Automated update for wiki content")

#### Options:
- `--select-wiki`: Interactively select a wiki from the configuration
- `--wiki WIKI_ID`: Specify a wiki by ID from the configuration
- `--api-url API_URL`: Specify a custom wiki API URL
- `--add-wiki`: Interactively add a new wiki to the configuration

## Configuration

### Main Configuration (`wiki_config.json`)
Contains predefined configurations for popular wikis with:
- Wiki names and API endpoints
- User agent strings
- Wiki-specific validation rules

### User Configuration (`user_wikis.json`)
Allows users to define custom wikis. Copy the sample file to get started:
```bash
cp user_wikis.json.sample user_wikis.json
```

Then edit `user_wikis.json` to add your custom wikis.

## Security Features

- **HTTPS Enforcement**: All API communication over HTTPS
- **Secure File Handling**: Temporary files with process-specific names
- **Configuration Security**: User configs with secure permissions (600)
- **Memory Management**: Secure clearing of sensitive data

## Validation Features

### Generic Validation (Always Applied)
- Content matching between local file and wiki page
- Proper formatting verification
- Spam keyword detection
- Edit summary validation

### Wiki-Specific Validation (Configurable)
- Related articles section (Arch Wiki)
- Infobox templates (Wikipedia)
- Navbox templates (Fandom)
- Custom patterns defined by user

## Examples

### Submit to Arch Wiki
```bash
python3 scripts/wiki_secure_submission.py --wiki archwiki "My Page" "content.md" "Initial page creation"
```

### Submit to Wikipedia
```bash
python3 scripts/wiki_secure_submission.py --wiki wikipedia "My Article" "article.md" "New article submission"
```

### Submit to Custom Wiki
```bash
python3 scripts/wiki_secure_submission.py --api-url "https://mywiki.example.com/api.php" "My Page" "content.md" "Update"
```

### Interactive Wiki Selection
```bash
python3 scripts/wiki_secure_submission.py --select-wiki "My Page" "content.md" "Edit summary"
```

## Adding Custom Wikis

### Method 1: Interactive Addition
```bash
python3 scripts/wiki_secure_submission.py --add-wiki "Page Title" "content_file.md" "Edit summary"
```

### Method 2: Manual Configuration
1. Copy the sample user configuration file:
   ```bash
   cp user_wikis.json.sample user_wikis.json
   ```

2. Edit `user_wikis.json` to add your wiki:
   ```json
   {
     "wikis": {
       "my_custom_wiki": {
         "name": "My Custom Wiki",
         "api_url": "https://mywiki.example.com/api.php",
         "user_agent": "WikiSecureBot/1.0 (My Custom Wiki)",
         "validation_rules": {
           "custom_rule_1": "Custom validation pattern 1",
           "custom_rule_2": "Custom validation pattern 2"
         }
       }
     }
   }
   ```

3. Use your custom wiki:
   ```bash
   python3 scripts/wiki_secure_submission.py --wiki my_custom_wiki "Page Title" "content_file.md" "Edit summary"
   ```

## Supported Wikis

The tool comes with predefined configurations for:

### Wikimedia Foundation Wikis
- Wikipedia (https://en.wikipedia.org)
- Wiktionary (https://en.wiktionary.org)
- Wikibooks (https://en.wikibooks.org)
- Wikiquote (https://en.wikiquote.org)
- Wikisource (https://en.wikisource.org)
- Wikiversity (https://en.wikiversity.org)
- Wikidata (https://www.wikidata.org)
- Wikimedia Commons (https://commons.wikimedia.org)

### Technology Wikis
- Arch Wiki (https://wiki.archlinux.org)
- Ubuntu Wiki (https://wiki.ubuntu.com)
- Debian Wiki (https://wiki.debian.org)
- Gentoo Wiki (https://wiki.gentoo.org)
- Fedora Wiki (https://fedoraproject.org/wiki)
- Python Wiki (https://wiki.python.org)

### Fandom Wikis
- Minecraft Wiki (https://minecraft.fandom.com)
- League of Legends Wiki (https://leagueoflegends.fandom.com)
- Harry Potter Wiki (https://harrypotter.fandom.com)
- Star Wars Wiki (https://starwars.fandom.com)
- Marvel Wiki (https://marvel.fandom.com)
- DC Comics Wiki (https://dc.fandom.com)

## Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Security

For security considerations and best practices, please see our [SECURITY_GUIDE.md](SECURITY_GUIDE.md).

## Authors

- **Your Name** - *Initial work* - [yourusername](https://github.com/yourusername)

## Acknowledgments

- Thanks to the MediaWiki community for their excellent API documentation
- Inspired by the need for secure, automated wiki content management