# CloudParty Detailed Setup Guide

## Overview

CloudParty is a user-friendly Windows application that provides a system tray interface for the powerful [copyparty](https://github.com/9001/copyparty) file server. It allows you to run a file sharing server without a visible console window, making it perfect for personal or small office use.

## Architecture

CloudParty consists of:
- **copyparty core**: The underlying file server written in Python
- **System tray application**: Windows-specific wrapper using pystray
- **Configuration system**: INI-style config files for easy setup
- **Web interface**: Modern dark-themed UI for administration

## System Requirements

### Minimum Requirements
- Windows 7 SP1 or later
- Python 3.8+ (for source installation)
- 512 MB RAM
- 100 MB disk space

### Recommended Requirements
- Windows 10 or 11
- Python 3.9+
- 1 GB RAM
- SSD storage for better performance

## Installation Methods

### Method 1: Pre-built Executable (Recommended)

1. **Download**: Get the latest `CloudParty.exe` from [Releases](https://github.com/kroryan/CloudParty/releases)
2. **Extract**: Place in a dedicated folder (e.g., `C:\CloudParty`)
3. **Run**: Double-click `CloudParty.exe`
4. **First Login**: Use default credentials `admin` / `admin`
5. **Change Password**: You will be prompted to change your password on first login

### Method 2: From Source

#### Prerequisites
```bash
# Install Python 3.8+
# Download from https://python.org

# Install required packages
pip install pystray pillow
```

#### Build Steps
```bash
# Clone repository
git clone https://github.com/kroryan/CloudParty.git
cd CloudParty

# Install dependencies
pip install -r requirements.txt

# Build executable (optional)
pyinstaller cloudparty.spec --clean

# Run directly
python cloudparty_launcher.py
```

## Configuration Deep Dive

### Global Section Options

#### Network Configuration
```ini
[global]
  # Single port
  p: 3923
  
  # Multiple ports (HTTP and HTTPS)
  p: 80,443
  
  # Interface binding
  i: ::        # All IPv4/IPv6
  i: 0.0.0.0   # IPv4 only
  i: 127.0.0.1 # Localhost only
```

#### Feature Flags
```ini
[global]
  # Core features
  e2dsa        # File indexing and search
  e2ts         # Media metadata extraction
  z            # Zeroconf/mDNS discovery
  qr           # QR code for mobile access
  
  # Security and privacy
  no-robots    # Prevent search engine indexing
  nih          # No info headers
  vague-403    # Hide file existence
  
  # Performance
  rmagic       # Better mimetype detection
  e2v          # Verify file integrity on startup
```

#### UI and Behavior
```ini
[global]
  theme: cloudparty    # Dark theme
  start_hidden: true   # Tray mode
  v                    # Verbose logging
```

### Accounts Section

#### First Run
On first run, CloudParty creates a default admin account:
- **Username**: `admin`
- **Password**: `admin`

You will be automatically redirected to change your password after first login.

#### User Management
```ini
[accounts]
  # Admin user (required for web interface)
  admin: SecurePassword123!

  # Regular users
  john: johnspass
  mary: maryspass

  # Guest access
  guest: guest
```

#### Password Security
- Use strong passwords (8+ characters minimum, 12+ recommended)
- Mix of uppercase, lowercase, numbers, symbols
- Avoid common words
- Default password will be changed on first login

### Volume Configuration

#### Basic Volume
```ini
[/shared]
  C:/SharedFiles
  accs:
    r: *          # Everyone can read
    rw: admin     # Admin full access
```

#### Advanced Volume with Flags
```ini
[/uploads]
  D:/Uploads
  accs:
    w: *          # Anonymous upload
    rw: admin     # Admin management
  flags:
    e2d           # Database enabled
    nodupe        # Reject duplicates
    magic         # File type detection
    gz            # Compression allowed
```

#### Permission Matrix

| Permission | Description | Use Case |
|------------|-------------|----------|
| `r` | Read/list/download | Public access |
| `w` | Write/upload | Upload areas |
| `rw` | Read + write | Shared workspaces |
| `m` | Move files | File organization |
| `d` | Delete files | Full control |
| `g` | Download only | Hidden listings |
| `a` | Admin access | Server management |
| `A` | All permissions | Super user |
| `*` | Everyone | Anonymous access |

## Advanced Configuration

### Database Configuration
```ini
[global]
  # Database location
  hist: C:/CloudParty/db
  
  # Database options
  dbd: acid     # Durability: acid/wal/yolo
  no_db_ip      # GDPR compliance
  forget_ip: 30 # Forget IPs after 30 days
```

### Upload Controls
```ini
[/uploads]
  C:/Uploads
  accs:
    w: *
  flags:
    # Size limits
    sz: 1k-100m    # 1KB to 100MB
    vmaxb: 10g     # Volume max 10GB
    
    # Rate limiting
    maxn: 100,10   # Max 100 uploads per 10 minutes
    maxb: 1g,300   # Max 1GB per 5 minutes
    
    # Upload behavior
    put_name: upload-{now}-{cip}.bin
    apnd_who: dw   # Who can append
```

### Media Processing
```ini
[global]
  # Thumbnail generation
  th_size: 200   # Thumbnail size
  th_crop: smart # Cropping mode
  
  # Audio processing
  mte: artist,title,album  # Extracted tags
  mth: duration,bitrate    # Hidden tags
```

## Security Best Practices

### Network Security
- Bind to specific interfaces when possible
- Use firewall rules to restrict access
- Enable HTTPS for remote access
- Use strong passwords

### File System Security
- Run as limited user account
- Restrict folder permissions
- Enable audit logging
- Regular backup procedures

### Access Control
```ini
# Secure configuration example
[global]
  i: 127.0.0.1    # Localhost only
  no-robots       # No search indexing
  vague-403       # Hide file info

[accounts]
  admin: VeryStrongPassword!

[/secure]
  C:/SecureData
  accs:
    rw: admin     # Admin only
```

## Performance Tuning

### For Large File Servers
```ini
[global]
  j: 4            # 4 CPU cores for I/O
  iobuf: 1048576  # 1MB I/O buffer
  
  # Disable heavy features
  # Comment out e2ts if not needed
```

### For High-traffic Sites
```ini
[global]
  # Connection limits
  nc: 100         # Max 100 clients
  
  # Caching
  cache: 3600     # Cache for 1 hour
  
  # Compression
  gz              # Enable gzip
```

### Memory Optimization
```ini
[global]
  # Reduce memory usage
  no_dirsz        # Don't calculate folder sizes
  dthumb          # Disable thumbnails
  dvthumb         # Disable video thumbnails
```

## Monitoring and Maintenance

### Log Files
- Console output via tray icon
- Web interface admin panel
- Log rotation with external tools

### Database Maintenance
```bash
# Rebuild search index
# Access via web interface or command line

# Clean old data
# Configure retention policies
```

### Backup Strategy
- Configuration files
- Database files (`*.db`, `*.hist`)
- User data (shared folders)
- Regular automated backups

## Troubleshooting Guide

### Startup Issues

#### "Port already in use"
```ini
# Change port in config
[global]
  p: 3924
```

#### "Permission denied"
- Run as administrator
- Check folder permissions
- Disable antivirus temporarily

#### "Module not found"
```bash
pip install pystray pillow
```

### Runtime Issues

#### High CPU usage
- Reduce concurrent connections
- Disable media indexing
- Check for antivirus interference

#### Upload failures
- Check disk space
- Verify write permissions
- Check file size limits

#### Web interface not loading
- Clear browser cache
- Check firewall settings
- Verify port configuration

### Debug Mode
```ini
[global]
  v              # Verbose logging
  vv             # Very verbose
  debug          # Debug mode
```

## Integration Examples

### Windows Service
```batch
# Install as service using NSSM
nssm install CloudParty "C:\CloudParty\CloudParty.exe"
nssm set CloudParty AppDirectory "C:\CloudParty"
nssm start CloudParty
```

### Docker Container
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 3923
CMD ["python", "cloudparty_launcher.py"]
```

### Reverse Proxy (nginx)
```nginx
server {
    listen 80;
    server_name files.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:3923;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Development

### Building from Source
```bash
# Development setup
pip install -e .

# Run tests
python -m pytest

# Build executable
pyinstaller cloudparty.spec
```

### Code Structure
```
cloudparty/
├── __main__.py          # Entry point
├── cfg.py              # Configuration parsing
├── httpsrv.py          # HTTP server
├── cloudparty_console.py  # Tray application
└── ...
```

### Contributing
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Submit pull requests

## FAQ

### Q: Can I run multiple instances?
A: Yes, use different ports and configuration files.

### Q: How do I enable HTTPS?
A: Use reverse proxy (nginx/caddy) or configure certificates.

### Q: What's the difference from copyparty?
A: CloudParty adds Windows tray interface and simplified configuration.

### Q: Can I use it on Linux/Mac?
A: The core copyparty works, but tray features require Windows.

### Q: How do I migrate from copyparty?
A: Copy your config file and adjust paths for Windows.

## Support and Resources

- [GitHub Issues](https://github.com/kroryan/CloudParty/issues)
- [copyparty Documentation](https://github.com/9001/copyparty)
- [Configuration Reference](docs/CONFIGURATION.md)
- [Community Forum](https://github.com/9001/copyparty/discussions)

---

*This guide is maintained by the CloudParty project. Last updated: January 2026*