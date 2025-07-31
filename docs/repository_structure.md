# Repository Structure

This document describes the structure of the Wiki Submission Tool repository.

## Root Directory

```
wiki-submission-tool/
├── CONTRIBUTING.md
├── LICENSE.md
├── README.md
├── SECURITY_GUIDE.md
├── wiki_credentials.conf.sample
├── .github/
├── docs/
└── scripts/
```

## .github Directory

Contains GitHub-specific configuration files.

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
└── workflows/
```

### ISSUE_TEMPLATE
- `bug_report.md` - Template for reporting bugs
- `feature_request.md` - Template for requesting features

### workflows
- Contains GitHub Actions workflows (to be added)

## docs Directory

Contains detailed documentation for the project.

```
docs/
└── repository_structure.md
```

- `repository_structure.md` - This document describing the repository structure

## scripts Directory

Contains all the executable scripts for wiki submission.

```
scripts/
├── archwiki_api_login.sh
├── archwiki_automated_submission.sh
├── archwiki_credentials.conf.sample
├── archwiki_get_csrf_token.sh
├── archwiki_submit_edit.sh
├── fix_bluetooth.sh
├── get_wiki_page.sh
├── README_ARCHWIKI_AUTOMATION.md
├── README_BASH_AUTOMATION.md
├── README_PYTHON_AUTOMATION.md
├── wiki_automated_submission.py
├── wiki_automated_submission.sh
├── wiki_secure_submission.py
└── wiki_secure_submission.sh
```

### ArchWiki Scripts
- `archwiki_api_login.sh` - Script for logging into ArchWiki API
- `archwiki_automated_submission.sh` - Automated submission script for ArchWiki
- `archwiki_credentials.conf.sample` - Sample credentials file for ArchWiki
- `archwiki_get_csrf_token.sh` - Script for getting CSRF token from ArchWiki
- `archwiki_submit_edit.sh` - Script for submitting edits to ArchWiki

### Utility Scripts
- `fix_bluetooth.sh` - Bluetooth troubleshooting script
- `get_wiki_page.sh` - Script for retrieving wiki page content

### Documentation
- `README_ARCHWIKI_AUTOMATION.md` - ArchWiki automation documentation
- `README_BASH_AUTOMATION.md` - Bash automation documentation
- `README_PYTHON_AUTOMATION.md` - Python automation documentation

### Main Scripts
- `wiki_automated_submission.py` - Python version of automated submission script
- `wiki_automated_submission.sh` - Bash version of automated submission script
- `wiki_secure_submission.py` - Python version of secure submission script
- `wiki_secure_submission.sh` - Bash version of secure submission script

## File Descriptions

### README.md
Main documentation file with overview, features, usage instructions, and requirements.

### CONTRIBUTING.md
Guidelines for contributing to the project.

### LICENSE.md
License information for the project.

### SECURITY_GUIDE.md
Security best practices and guidelines for using the tool.

### wiki_credentials.conf.sample
Sample configuration file for credentials.