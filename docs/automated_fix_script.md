# Automated Fix Script Documentation

This document describes the automated Bluetooth fix script included in the Wiki Submission Tool.

## Overview

The `fix_bluetooth.sh` script is designed to automatically diagnose and fix common Bluetooth connectivity issues on Linux systems, particularly Arch Linux with KDE Plasma.

## Features

- Automatic detection of Bluetooth service status
- Service enablement and restart
- User group management for Bluetooth access
- Configuration file modification
- Kernel module management
- Hardware detection and verification
- Detailed logging of all actions

## Usage

### Basic Usage
```bash
chmod +x scripts/fix_bluetooth.sh
sudo ./scripts/fix_bluetooth.sh
```

### Verbose Mode
```bash
sudo ./scripts/fix_bluetooth.sh -v
```

### Dry Run Mode
```bash
sudo ./scripts/fix_bluetooth.sh -d
```

## Script Workflow

### 1. Service Status Check
- Checks if the Bluetooth service is running
- Enables the service if it's disabled
- Restarts the service if needed

### 2. User Permissions
- Verifies the current user is in the lp group
- Adds the user to the lp group if missing
- Applies group changes without requiring logout

### 3. Configuration Verification
- Checks `/etc/bluetooth/main.conf` for AutoEnable setting
- Enables AutoEnable if it's disabled or commented out

### 4. Kernel Modules
- Verifies required Bluetooth kernel modules are loaded
- Loads missing modules (btusb, bnep, rfcomm)
- Ensures zstd module is loaded for firmware decompression

### 5. Hardware Detection
- Lists USB Bluetooth devices
- Lists PCIe Bluetooth devices
- Verifies Bluetooth interfaces are available

### 6. Service Restart
- Restarts the Bluetooth service to apply all changes
- Verifies the service is running correctly

## Supported Hardware

The script is designed to work with a wide range of Bluetooth hardware, with special support for:

- Realtek Bluetooth adapters (5.3 and newer)
- Intel Bluetooth adapters
- Broadcom Bluetooth adapters
- Generic USB Bluetooth dongles

## Troubleshooting

### Common Issues

#### Authentication Failed Errors
The script addresses "Authentication Failed (0x05)" errors by:
- Ensuring the user is in the lp group
- Loading required kernel modules
- Resetting the Bluetooth adapter

#### Firmware Issues
For Realtek adapters with firmware loading issues:
- Loads the zstd module for firmware decompression
- Verifies firmware files exist in `/lib/firmware/rtl_bt/`

#### Service Not Starting
The script ensures:
- Proper service configuration
- Correct file permissions
- Required dependencies are installed

### Log Files
All actions are logged to `/var/log/bluetooth-fix.log` with timestamps and detailed information.

## Customization

### Configuration Options
The script can be customized by modifying these variables at the top of the file:

- `LOG_FILE` - Path to the log file
- `VERBOSE` - Enable verbose output
- `DRY_RUN` - Enable dry run mode

### Adding New Fixes
To add new fixes:
1. Create a new function for the fix
2. Add the function to the main execution flow
3. Ensure proper error handling
4. Add logging for the new fix

## Requirements

- bash 4.0+
- systemd
- bluez
- bluez-utils
- curl
- python3 (for JSON parsing)

## Security Considerations

- The script requires sudo privileges for system modifications
- All changes are logged for audit purposes
- No credentials or sensitive information are stored
- Temporary files are securely deleted

## Integration

The script can be integrated into:
- System startup scripts
- User login scripts
- Automated deployment systems
- CI/CD pipelines for system setup

## Limitations

- Requires sudo privileges
- Designed primarily for Arch Linux (may work on other distributions with modifications)
- May require manual intervention for hardware-specific issues
- Does not handle all possible Bluetooth issues

## Contributing

To contribute improvements to the script:
1. Fork the repository
2. Create a new branch for your changes
3. Test thoroughly on multiple systems
4. Submit a pull request with detailed information about your changes