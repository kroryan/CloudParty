# CloudParty Configuration Guide

This document provides a comprehensive guide to configuring CloudParty.

## Table of Contents

- [Configuration File Overview](#configuration-file-overview)
- [Global Section](#global-section)
- [Accounts Section](#accounts-section)
- [Volume Sections](#volume-sections)
- [Complete Configuration Examples](#complete-configuration-examples)
- [Advanced Configuration](#advanced-configuration)
- [Environment-Specific Configurations](#environment-specific-configurations)

## Configuration File Overview

CloudParty uses an INI-style configuration file named `cloudparty.conf`. This file must be placed in the same directory as the CloudParty executable.

### File Location

```
CloudParty/
|-- CloudParty.exe
|-- cloudparty.conf          <-- Your configuration file
|-- cloudparty.example.conf  <-- Example template
```

### Basic Syntax Rules

1. **Comments**: Lines starting with `#` are comments
2. **Sections**: Defined with `[section_name]`
3. **Key-Value Pairs**: Use `key: value` format
4. **Indentation**: Use 2 spaces for nested items
5. **Flags**: Can be listed without values (e.g., `e2dsa`)

### Configuration Sections

The configuration file has three main section types:

1. `[global]` - Server-wide settings
2. `[accounts]` - User accounts
3. `[/path]` - Volume definitions (shared folders)

## Global Section

The `[global]` section contains server-wide settings.

### Network Settings

```ini
[global]
  # Port(s) to listen on
  # Single port:
  p: 3923

  # Multiple ports (comma-separated):
  p: 3923,8080,443

  # Interface to bind to
  # All interfaces (IPv4 + IPv6):
  i: ::

  # All IPv4 interfaces only:
  i: 0.0.0.0

  # Localhost only (most secure):
  i: 127.0.0.1

  # Specific IP address:
  i: 192.168.1.100
```

### Interface Options Explained

| Value | IPv4 | IPv6 | Local | Remote | Use Case |
|-------|------|------|-------|--------|----------|
| `::` | Yes | Yes | Yes | Yes | Default, all access |
| `0.0.0.0` | Yes | No | Yes | Yes | IPv4 only |
| `127.0.0.1` | Yes | No | Yes | No | Local access only |
| `::1` | No | Yes | Yes | No | IPv6 localhost |
| `192.168.x.x` | Yes | No | No | LAN | Specific network |

### Feature Flags

Feature flags enable optional functionality:

```ini
[global]
  # File indexing - enables fast search
  e2dsa

  # Media metadata indexing - extracts tags from audio/video
  e2ts

  # Zeroconf/mDNS - automatic network discovery
  z

  # QR code - display QR code on login page
  qr

  # Multiple flags on one line:
  e2dsa, e2ts, z, qr
```

### Feature Flag Details

| Flag | Description | Performance Impact |
|------|-------------|-------------------|
| `e2dsa` | File indexing and search | Initial scan, then minimal |
| `e2ts` | Media tag extraction | CPU intensive during scan |
| `z` | Zeroconf/mDNS discovery | Minimal |
| `qr` | QR code on login | None |

### Appearance Settings

```ini
[global]
  # Theme selection
  # CloudParty dark theme (recommended):
  theme: cloudparty

  # Built-in themes (0-9):
  theme: 0  # Light
  theme: 1  # Dark
  theme: 6  # Hacker dark
```

### Startup Behavior

```ini
[global]
  # Start with console hidden (default: true)
  start_hidden: true

  # Note: Console is always hidden in tray mode
  # Access logs via Admin Panel -> Console button
```

## Accounts Section

The `[accounts]` section defines user credentials.

### Basic User Definition

```ini
[accounts]
  # Format: username: password
  admin: MySecurePassword123
  guest: guestpass
  john: johns_password
```

### Username Rules

- Alphanumeric characters, underscore, and hyphen
- Case-sensitive
- No spaces allowed
- Reserved names: `*` (means "everyone")

### Password Guidelines

- Any characters allowed
- Case-sensitive
- Minimum recommended length: 8 characters
- Stored in plain text in config file (secure file permissions!)

### Special User: admin

The `admin` user has special privileges:
- Access to the Admin Panel
- Can manage users and volumes via web interface
- Can view server console/logs

```ini
[accounts]
  # Always define an admin user
  admin: VerySecurePassword!@#
```

## Volume Sections

Volumes define shared folders accessible via the web interface.

### Basic Volume Definition

```ini
# Format: [/url_path]
[/documents]
  D:/MyDocuments
  accs:
    r: *
    rw: admin
```

This creates a volume:
- Accessible at: `http://localhost:3923/documents/`
- Mapped to: `D:/MyDocuments` on the server
- Everyone can read, admin can read/write

### Volume Section Structure

```ini
[/mount_path]           # URL path (must start with /)
  /local/filesystem/path  # Actual folder on server
  accs:                   # Access control section
    permission: users     # Permission assignments
  flags:                  # Optional flags
    flag1, flag2
```

### Path Formats

```ini
# Windows paths (use forward slashes):
[/files]
  D:/SharedFiles

# Or backslashes (escaped):
[/files]
  D:\SharedFiles

# Relative paths (relative to exe location):
[/data]
  ./data

# Network paths (UNC):
[/network]
  //server/share
```

### Permission Types

| Permission | Meaning | Allows |
|------------|---------|--------|
| `r` | Read | List folders, download files |
| `w` | Write | Upload files |
| `rw` | Read+Write | Both above |
| `m` | Move | Move/rename files |
| `d` | Delete | Delete files/folders |
| `rwmd` | Full | All of the above |
| `a` | Admin | Server admin operations |
| `g` | Get | Download only (no listing) |
| `G` | Get+ | Download + hidden listing |

### User Specifiers

```ini
accs:
  # Everyone (including anonymous):
  r: *

  # Single user:
  rw: admin

  # Multiple users (space-separated):
  rw: admin john mary

  # Combination:
  r: *          # Everyone can read
  rw: admin     # Admin can also write
  d: admin      # Only admin can delete
```

### Permission Examples

#### Public Read-Only Library

```ini
[/library]
  D:/PublicLibrary
  accs:
    r: *           # Anyone can browse and download
```

#### Private User Folders

```ini
[/john-private]
  D:/Users/John/Private
  accs:
    rwmd: john     # Only John has full access
    r: admin       # Admin can view but not modify
```

#### Public Upload Box

```ini
[/uploads]
  D:/Uploads
  accs:
    w: *           # Anyone can upload
    rw: admin      # Admin can manage
  flags:
    nodupe         # Reject duplicate uploads
```

#### Team Collaboration Folder

```ini
[/team-project]
  D:/Projects/TeamAlpha
  accs:
    r: *           # Everyone can view
    rw: alice bob charlie  # Team members can edit
    d: alice       # Only Alice can delete
```

### Volume Flags

```ini
[/flagged-volume]
  D:/SomeFolder
  accs:
    rw: admin
  flags:
    e2d            # Enable file database
    nodupe         # Reject duplicate uploads
    e2ts           # Enable media tag scanning
    nolist         # Hide folder listing
```

| Flag | Description |
|------|-------------|
| `e2d` | Enable upload database for this volume |
| `nodupe` | Reject files that already exist (by hash) |
| `e2ts` | Enable media metadata extraction |
| `nolist` | Hide directory listing (direct links only) |
| `dk` | Enable directory keys (for sharing) |
| `fk` | Enable file keys (for sharing) |

## Complete Configuration Examples

### Minimal Configuration

```ini
# Minimal CloudParty configuration

[global]
  p: 3923
  i: ::

[accounts]
  admin: admin123

[/]
  D:/SharedFiles
  accs:
    rw: admin
```

### Home Server Configuration

```ini
# Home server with multiple users

[global]
  p: 3923
  i: ::
  theme: cloudparty
  e2dsa, e2ts, z, qr

[accounts]
  admin: SuperSecureAdminPass!
  family: familypass
  guest: guestpass

# Main shared folder
[/shared]
  D:/FamilyFiles
  accs:
    r: *
    rw: admin family

# Media library
[/media]
  D:/Media
  accs:
    r: *
    rw: admin
  flags:
    e2ts

# Private admin folder
[/admin-only]
  D:/AdminFiles
  accs:
    rwmd: admin

# Guest upload folder
[/guest-uploads]
  D:/Uploads/Guest
  accs:
    w: guest
    rw: admin
  flags:
    nodupe
```

### Small Office Configuration

```ini
# Small office file server

[global]
  p: 80
  i: 0.0.0.0
  theme: cloudparty
  e2dsa

[accounts]
  admin: AdminP@ssw0rd!
  manager: ManagerPass
  employee1: Emp1Pass
  employee2: Emp2Pass
  contractor: ContractorPass

# Company documents
[/documents]
  E:/CompanyDocs
  accs:
    r: manager employee1 employee2
    rw: admin manager
    d: admin

# Project files
[/projects]
  E:/Projects
  accs:
    rw: admin manager employee1 employee2

# Contractor deliverables (upload only)
[/contractor-uploads]
  E:/Contractor
  accs:
    w: contractor
    rw: admin manager
  flags:
    nodupe

# Public downloads
[/public]
  E:/Public
  accs:
    r: *
    rw: admin
```

### Development Server Configuration

```ini
# Development/testing server

[global]
  p: 8080
  i: 127.0.0.1
  theme: cloudparty
  e2dsa

[accounts]
  admin: devadmin
  dev: devpass

# Source code
[/code]
  C:/Development/Projects
  accs:
    rwmd: admin dev

# Build artifacts
[/builds]
  C:/Development/Builds
  accs:
    r: *
    rw: admin dev

# Logs
[/logs]
  C:/Development/Logs
  accs:
    r: admin dev
```

## Advanced Configuration

### Multiple Ports

Listen on multiple ports for different purposes:

```ini
[global]
  p: 80,443,8080
  i: ::
```

### Restricting to Specific Network

Only accessible from specific subnet:

```ini
[global]
  p: 3923
  i: 192.168.1.100  # Server's IP on the network
```

### Localhost Only (Maximum Security)

Only accessible from the same machine:

```ini
[global]
  p: 3923
  i: 127.0.0.1
```

## Environment-Specific Configurations

### Behind a Reverse Proxy

When CloudParty is behind nginx, Apache, or similar:

```ini
[global]
  p: 8080           # Internal port
  i: 127.0.0.1      # Only accept local connections
  theme: cloudparty
```

Example nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name files.example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Environment

When running in Docker:

```ini
[global]
  p: 3923
  i: 0.0.0.0        # Accept all (Docker handles network isolation)
  theme: cloudparty

[/data]
  /data             # Mounted volume in container
  accs:
    rw: admin
```

## Configuration Best Practices

### Security

1. **Strong Passwords**: Use complex passwords for all accounts
2. **Least Privilege**: Only grant necessary permissions
3. **Secure File**: Protect `cloudparty.conf` file permissions
4. **Firewall**: Use firewall rules to restrict access
5. **HTTPS**: Use reverse proxy with SSL for production

### Performance

1. **File Indexing**: Enable `e2dsa` only if you need search
2. **Media Tags**: Enable `e2ts` only for media libraries
3. **Multiple Ports**: Use single port unless specifically needed

### Maintenance

1. **Backups**: Regularly backup your configuration file
2. **Comments**: Add comments to document your setup
3. **Testing**: Test configuration changes before deployment

## Troubleshooting Configuration

### Common Issues

**Port Already in Use**
```
Error: Port 3923 is already in use
```
Solution: Change the port number or stop the conflicting application.

**Path Not Found**
```
Error: Volume path does not exist
```
Solution: Verify the path exists and is accessible.

**Permission Denied**
```
Error: Cannot access configuration file
```
Solution: Check file permissions on `cloudparty.conf`.

### Validating Configuration

To test your configuration:

1. Start CloudParty from command line to see errors:
   ```bash
   python cloudparty_launcher.py
   ```

2. Check the console output for warnings

3. Access the Admin Panel to verify settings

## Configuration File Template

```ini
# ============================================================
# CloudParty Configuration File
# ============================================================
#
# Documentation: https://github.com/kroryan/CloudParty
#
# ============================================================

# ------------------------------------------------------------
# Global Settings
# ------------------------------------------------------------
[global]
  # Network
  p: 3923                    # Port number
  i: ::                      # Interface (:: = all)

  # Appearance
  theme: cloudparty          # Theme name

  # Features (uncomment to enable)
  # e2dsa                    # File indexing
  # e2ts                     # Media tags
  # z                        # Zeroconf
  # qr                       # QR code

# ------------------------------------------------------------
# User Accounts
# ------------------------------------------------------------
[accounts]
  admin: CHANGE_THIS_PASSWORD

# ------------------------------------------------------------
# Volumes (Shared Folders)
# ------------------------------------------------------------

# Example: Root volume
[/]
  D:/SharedFiles
  accs:
    r: *
    rw: admin

# Add more volumes below...
```

---

For more information, see the main [README.md](../README.md) or visit the [GitHub repository](https://github.com/kroryan/CloudParty).
