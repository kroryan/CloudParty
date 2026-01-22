# CloudParty

**Your Personal Cloud Storage, Simplified.**
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/kroryan/CloudParty)



CloudParty is a modern, self-hosted personal cloud server designed for simplicity. Think of it as your own Nextcloud or Google Drive, but without the complex setup and configuration headaches. Just run the executable and you have your own "secure" file sharing server. I mean i do what i can but im not a professional so please use it at your own risk, i would not expose this to the internet but its okey to use it with tailscale.

![CloudParty](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## What is CloudParty?

CloudParty started as a fork of the excellent [copyparty](https://github.com/9001/copyparty) project, but has evolved into its own standalone application with a focus on:

- **Zero Configuration**: Download, run, done. No complicated setup required.
- **Windows-First**: Optimized for Windows with system tray integration.
- **Beautiful UI**: Modern dark blue theme that's easy on the eyes.
- **Web-Based Admin**: Manage everything from your browser.
- **Personal Cloud**: Host your own files and share them securely.

### CloudParty vs Nextcloud

| Feature | CloudParty | Nextcloud |
|---------|------------|-----------|
| Installation | Single exe | Server + Database + PHP |
| Configuration | Minimal | Extensive |
| Resource Usage | Light | Heavy |
| Learning Curve | Minutes | Hours/Days |
| Target User | Personal/Small Teams | Enterprise |

### CloudParty vs copyparty

CloudParty builds upon copyparty with these enhancements:

| Feature | CloudParty | copyparty |
|---------|------------|-----------|
| GUI Admin Panel | Floating admin button | None (CLI/config only) |
| First-Time Setup | Web wizard | Manual config |
| User Management | Web interface | Config file |
| Volume Management | Browser-based | Config file |
| System Tray | Native integration | External tools |
| Theme | Modern blue theme | Multiple themes |
| Default Auth | Required | Optional |

## Features

- **System Tray Application**: Runs silently in the background with easy access from system tray
- **Web-Based Admin Panel**: Manage users, volumes, and settings from your browser
- **Modern Dark Theme**: Beautiful dark blue interface that's easy on the eyes
- **User Management**: Create, edit, and delete users with granular permissions
- **Volume Management**: Add folders to share directly from the web interface
- **Folder Browser**: Browse and select server folders without leaving the browser
- **Real-time Console**: View server logs in real-time from the admin panel
- **Secure by Default**: Password-protected access with admin/user roles
- **No Terminal Visible**: Console is completely hidden, accessible only via web

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Admin Panel](#admin-panel)
- [User Management](#user-management)
- [Volume Management](#volume-management)
- [Permissions](#permissions)
- [Building from Source](#building-from-source)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Installation

### Pre-built Executable (Recommended)

1. Download the latest `CloudParty.exe` from the [Releases](https://github.com/kroryan/CloudParty/releases) page
2. Place it in a folder of your choice
3. Copy `cloudparty.example.conf` to `cloudparty.conf`
4. Edit `cloudparty.conf` with your settings
5. Run `CloudParty.exe`

### From Source

```bash
# Clone the repository
git clone https://github.com/kroryan/CloudParty.git
cd CloudParty

# Install dependencies
pip install -r requirements.txt

# Run directly
python cloudparty_launcher.py

# Or build executable
pyinstaller cloudparty.spec --clean
```

## Quick Start

1. **Create Configuration File**

   Copy the example configuration:
   ```
   cloudparty.example.conf -> cloudparty.conf
   ```

2. **Edit Configuration**

   Open `cloudparty.conf` and modify:
   - Set your admin password
   - Add your shared folders
   - Configure the port (default: 3923)

3. **Run CloudParty**

   Double-click `CloudParty.exe`. The icon will appear in your system tray.

4. **Access Web Interface**

   Open your browser and go to:
   ```
   http://localhost:3923/
   ```

5. **Login**

   Use your admin credentials to log in.

## Configuration

CloudParty uses a simple INI-style configuration file (`cloudparty.conf`).

### Configuration File Location

The configuration file must be in the same directory as `CloudParty.exe`.

### Basic Configuration Structure

```ini
# CloudParty Configuration File

[global]
  # Port to listen on
  p: 3923

  # Interface to bind (:: = all IPv4/IPv6)
  i: ::

  # Theme: cloudparty, 0 (light), 1 (dark)
  theme: cloudparty

  # Features (comma-separated or one per line)
  e2dsa          # File indexing
  e2ts           # Media metadata indexing
  z              # Zeroconf/mDNS
  qr             # Show QR code on login

[accounts]
  admin: YourSecurePassword123
  guest: guestpass

[/]
  D:/SharedFiles
  accs:
    r: *         # Everyone can read
    rw: admin    # Admin has full access

[/private]
  D:/PrivateData
  accs:
    rw: admin    # Only admin can access
```

### Global Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `p` | Port number(s) to listen on | `3923` |
| `i` | Interface to bind to | `::` (all) |
| `theme` | UI theme | `cloudparty` |
| `e2dsa` | Enable file indexing | disabled |
| `e2ts` | Enable media tag indexing | disabled |
| `z` | Enable Zeroconf/mDNS | disabled |
| `qr` | Show QR code on login | disabled |

### Interface Options

| Value | Description |
|-------|-------------|
| `::` | All IPv4 and IPv6 interfaces |
| `0.0.0.0` | All IPv4 interfaces only |
| `127.0.0.1` | Localhost only |
| `192.168.1.100` | Specific IP address |

### Theme Options

| Value | Description |
|-------|-------------|
| `cloudparty` | Dark blue theme (default) |
| `0` | Light theme |
| `1` | Dark theme |
| `2-9` | Other copyparty themes |

## Admin Panel

Access the admin panel at:
```
http://localhost:3923/?cloudparty_admin
```

You must be logged in as `admin` to access the admin panel.

### Admin Panel Sections

1. **Users**: Manage user accounts
2. **Volumes**: Manage shared folders
3. **Config**: Server settings

### Console

A floating "Console" button appears in the bottom-right corner when logged in as admin. Click it to view real-time server logs.

## User Management

### Adding a User via Web Interface

1. Go to Admin Panel -> Users
2. Click "+ Add User"
3. Enter username and password
4. Click "Add User"

### Adding a User via Configuration File

```ini
[accounts]
  username: password
  admin: admin123
  john: johns_password
  guest: guest
```

### User Roles

- **admin**: Full access to admin panel and all features
- **Regular users**: Access based on volume permissions

## Volume Management

Volumes are shared folders that appear in the web interface.

### Adding a Volume via Web Interface

1. Go to Admin Panel -> Volumes
2. Click "+ Add Volume"
3. Enter:
   - **Mount Path**: URL path (e.g., `/myfiles`)
   - **Local Path**: Server folder path (e.g., `D:/MyFiles`)
4. Set permissions
5. Click "Add Volume"

You can also use the "Browse..." button to navigate and select folders on the server.

### Adding a Volume via Configuration File

```ini
[/myfiles]
  D:/MyFiles
  accs:
    r: *
    rw: admin
```

### Volume Configuration Format

```ini
[/mount_path]
  /path/to/local/folder
  accs:
    permission: user1 user2
    permission: *
  flags:
    flag1, flag2
```

## Permissions

### Permission Types

| Permission | Description |
|------------|-------------|
| `r` | Read (list folders, download files) |
| `w` | Write (upload files) |
| `rw` | Read + Write |
| `m` | Move files/folders |
| `d` | Delete files/folders |
| `rwmd` | Full access (read, write, move, delete) |
| `a` | Admin access |

### User Specifiers

| Value | Description |
|-------|-------------|
| `*` | Everyone (including anonymous) |
| `username` | Specific user |
| `user1 user2` | Multiple users (space-separated) |

### Permission Examples

```ini
# Everyone can read, admin can do everything
accs:
  r: *
  rwmd: admin

# Only logged-in users can read
accs:
  r: admin guest john

# Public upload folder (write-only for guests)
accs:
  w: *
  rw: admin

# Private folder for specific users
accs:
  rw: john mary
```

## Volume Flags

Optional flags can be added to volumes:

```ini
[/uploads]
  D:/Uploads
  accs:
    w: *
    rw: admin
  flags:
    nodupe       # Reject duplicate files
    e2d          # Enable upload database
```

### Available Flags

| Flag | Description |
|------|-------------|
| `e2d` | Enable file database for this volume |
| `nodupe` | Reject duplicate file uploads |
| `e2ts` | Enable media tag scanning |
| `nolist` | Hide folder contents (direct links only) |

## Building from Source

### Requirements

- Python 3.10+
- pip packages: `pystray`, `pillow`, `copyparty`

### Build Steps

```bash
# Install dependencies
pip install pystray pillow pyinstaller

# Install copyparty in development mode
pip install -e .

# Build executable
pyinstaller cloudparty.spec --clean
```

The executable will be created in the `dist/` folder.

### Build Configuration

The `cloudparty.spec` file controls the build process:

```python
# Key settings
console=False    # No console window
upx=True         # Compress executable
icon=['cloudparty.ico']  # Application icon
```

## Troubleshooting

### Application Won't Start

1. **Check Configuration**: Ensure `cloudparty.conf` exists and is valid
2. **Check Port**: Make sure port 3923 is not in use
3. **Check Logs**: Look for errors in the Console (if accessible)

### Can't Access Web Interface

1. **Check Firewall**: Allow port 3923 in Windows Firewall
2. **Check URL**: Use `http://localhost:3923/`
3. **Check Interface**: If using specific IP, use that in the URL

### Volumes Not Showing

1. **Check Paths**: Ensure the local paths exist
2. **Check Permissions**: User must have read access to the volume
3. **Restart**: Some changes require a restart

### Login Issues

1. **Check Credentials**: Verify username/password in config
2. **Case Sensitive**: Usernames and passwords are case-sensitive
3. **Clear Cookies**: Try clearing browser cookies

### Build Errors

1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **Python Version**: Ensure Python 3.10+
3. **Clean Build**: Use `--clean` flag with pyinstaller

## File Structure

```
CloudParty/
|-- cloudparty_launcher.py    # Main application entry point
|-- cloudparty.conf           # Configuration file (create from example)
|-- cloudparty.example.conf   # Example configuration
|-- cloudparty.ico            # Application icon
|-- cloudparty.spec           # PyInstaller build configuration
|-- copyparty/                # Core server code
|   |-- __init__.py
|   |-- __main__.py
|   |-- httpcli.py            # HTTP client handler
|   |-- httpsrv.py            # HTTP server
|   |-- authsrv.py            # Authentication
|   |-- cloudparty_console.py # Console log capture
|   +-- web/                  # Web interface files
|       |-- cloudparty_admin.html
|       |-- cloudparty_login.html
|       |-- cloudparty.css
|       |-- browser.html
|       +-- ...
|-- docs/                     # Documentation
+-- dist/                     # Built executable (after build)
```

## Security Considerations

1. **Change Default Password**: Always change the admin password
2. **Use HTTPS**: Consider using a reverse proxy with SSL
3. **Firewall**: Only expose necessary ports
4. **Permissions**: Use least-privilege principle for users
5. **Updates**: Keep CloudParty updated

## API Reference

CloudParty exposes a JSON API for admin operations:

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/?cloudparty_api=logs` | GET | Get server logs |
| `/?cloudparty_api=browse_folders` | GET | Browse server folders |
| `/?cloudparty_api=add_user` | POST | Add new user |
| `/?cloudparty_api=edit_user` | POST | Edit user |
| `/?cloudparty_api=delete_user` | POST | Delete user |
| `/?cloudparty_api=add_volume` | POST | Add new volume |
| `/?cloudparty_api=edit_volume` | POST | Edit volume |
| `/?cloudparty_api=delete_volume` | POST | Delete volume |
| `/?cloudparty_api=save_settings` | POST | Save settings |

### Example API Call

```javascript
fetch('/?cloudparty_api=add_volume', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        mount_path: '/newshare',
        source_path: 'D:/NewFolder',
        permissions: {'rw': 'admin', 'r': '*'}
    })
});
```

## System Tray Options

Right-click the CloudParty icon in the system tray:

- **Open in Browser**: Opens the web interface in your default browser
- **Reload Config**: Reloads the configuration file without restarting
- **Exit**: Shuts down the server and exits

## Troubleshooting

### Common Issues

#### Server Won't Start
- **Check Configuration**: Ensure `cloudparty.conf` exists and has valid syntax
- **Port Conflicts**: Verify port 3923 is not in use by another application
- **Permissions**: Make sure the user has read/write access to shared folders
- **Firewall**: Allow CloudParty through Windows Firewall

#### Can't Access Web Interface
- **Check URL**: Use `http://localhost:3923/` (not HTTPS)
- **Port Settings**: Verify the port in configuration matches your access URL
- **Interface Binding**: If bound to `127.0.0.1`, only localhost access is allowed

#### Upload Issues
- **Permissions**: Ensure write permissions are set for the target folder
- **Disk Space**: Check available disk space on the server
- **File Size Limits**: Large files may need chunked upload settings

#### Performance Problems
- **Database Indexing**: Disable `e2dsa` and `e2ts` if scanning is slow
- **CPU Usage**: Reduce concurrent uploads with `-j 1` if needed
- **Memory**: Monitor RAM usage during large file operations

### Logs and Debugging

- **Console Logs**: Right-click tray icon → Show/Hide Console
- **Web Console**: Access Admin Panel → Console tab
- **Verbose Logging**: Add `v` flag to global section for detailed logs

### Reset Configuration

If configuration issues persist:
1. Delete `cloudparty.conf`
2. Copy `cloudparty.example.conf` to `cloudparty.conf`
3. Modify with minimal settings
4. Restart CloudParty

### Getting Help

- Check the [copyparty documentation](https://github.com/9001/copyparty)
- Search existing [GitHub Issues](https://github.com/kroryan/CloudParty/issues)
- Create a new issue with your configuration and error logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- [copyparty](https://github.com/9001/copyparty) - The underlying file server
- [pystray](https://github.com/moses-palmer/pystray) - System tray functionality
- [Pillow](https://python-pillow.org/) - Image processing

## Support

- [GitHub Issues](https://github.com/kroryan/CloudParty/issues) - Bug reports and feature requests

---

Made with love by the CloudParty team
## Known Issues

**No default volume path**

CloudParty no longer pre-populates a local filesystem path in `cloudparty.conf`. After first launch, add your share path in the admin UI or edit the config manually under a volume section.
