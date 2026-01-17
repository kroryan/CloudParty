#!/usr/bin/env python3
# coding: utf-8
"""
CloudParty Launcher - Tray Application
A system tray wrapper for copyparty that allows running without visible console
and supports configuration file-based setup.
"""

import ctypes
import json
import os
import sys
import threading
import time
import subprocess
from pathlib import Path

# Thread-safe flag for running state
_running_lock = threading.Lock()
_running = False

def set_running(value):
    global _running
    with _running_lock:
        _running = value

def is_running():
    with _running_lock:
        return _running

# Check for optional dependencies early
HAVE_PYSTRAY = False
HAVE_PIL = False

try:
    import pystray
    HAVE_PYSTRAY = True
except ImportError:
    pass

try:
    from PIL import Image, ImageDraw
    HAVE_PIL = True
except ImportError:
    pass

# Determine if we're running as a frozen executable
FROZEN = getattr(sys, 'frozen', False)
if FROZEN:
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

CONFIG_FILE = APP_DIR / "cloudparty.conf"
EXAMPLE_CONFIG = APP_DIR / "cloudparty.example.conf"

# Windows console handling
if sys.platform == 'win32':
    try:
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        user32 = ctypes.WinDLL('user32', use_last_error=True)
    except Exception as e:
        print(f"[CloudParty] Warning: Could not load Windows DLLs: {e}")
        kernel32 = None
        user32 = None
    
    SW_HIDE = 0
    SW_SHOW = 5
    SW_MINIMIZE = 6
    
    # Console close event handler constants
    CTRL_C_EVENT = 0
    CTRL_BREAK_EVENT = 1
    CTRL_CLOSE_EVENT = 2
    CTRL_LOGOFF_EVENT = 5
    CTRL_SHUTDOWN_EVENT = 6
    
    # Handler function type
    HANDLER_ROUTINE = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)
    
    # Global reference to prevent garbage collection
    _console_handler = None
    
    def _console_ctrl_handler(ctrl_type):
        """Handle console control events to prevent closing the app."""
        if ctrl_type == CTRL_CLOSE_EVENT:
            # User clicked X on console - hide instead of close
            hide_console()
            return True  # Handled - don't terminate
        elif ctrl_type in (CTRL_C_EVENT, CTRL_BREAK_EVENT):
            # Allow Ctrl+C to work normally
            return False
        elif ctrl_type in (CTRL_LOGOFF_EVENT, CTRL_SHUTDOWN_EVENT):
            # Allow system shutdown/logoff
            return False
        return False
    
    def setup_console_handler():
        """Set up handler to intercept console close button."""
        global _console_handler
        if kernel32:
            try:
                _console_handler = HANDLER_ROUTINE(_console_ctrl_handler)
                kernel32.SetConsoleCtrlHandler(_console_handler, True)
            except Exception as e:
                print(f"[CloudParty] Warning: Could not set console handler: {e}")
    
    def get_console_window():
        """Get the console window handle."""
        if kernel32:
            return kernel32.GetConsoleWindow()
        return 0
    
    def show_console():
        """Show the console window."""
        hwnd = get_console_window()
        if hwnd and user32:
            result = user32.ShowWindow(hwnd, SW_SHOW)
            error = ctypes.get_last_error()
            if error:
                print(f"[CloudParty] Warning: ShowWindow error {error}")
            return result != 0
        return False
    
    def hide_console():
        """Hide the console window."""
        hwnd = get_console_window()
        if hwnd and user32:
            result = user32.ShowWindow(hwnd, SW_HIDE)
            return result != 0
        return False
    
    def is_console_visible():
        """Check if console window is visible."""
        hwnd = get_console_window()
        if hwnd and user32:
            return user32.IsWindowVisible(hwnd) != 0
        return True
else:
    def get_console_window():
        return None
    def show_console():
        return False
    def hide_console():
        return False
    def is_console_visible():
        return True
    def setup_console_handler():
        pass  # Not needed on non-Windows


def load_config():
    """Load configuration from cloudparty.conf file."""
    config = {
        'port': 3923,
        'interface': '::',
        'accounts': {},
        'volumes': [],
        'start_hidden': True,
        'start_minimized': False,
        'auto_start': False,
        'enable_ssl': False,
        'ssl_cert': '',
        'ssl_key': '',
        'extra_args': [],
        'log_level': 'normal',
        'theme': 'cloudparty',  # Use our custom dark blue theme
    }
    
    if not CONFIG_FILE.exists():
        print(f"[CloudParty] Config file not found: {CONFIG_FILE}")
        print(f"[CloudParty] Creating example config at: {EXAMPLE_CONFIG}")
        create_example_config()
        return None
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the config file (INI-like format compatible with copyparty)
        current_section = 'global'
        current_volume_path = None
        parsed = {'global': {}, 'accounts': {}, 'volumes': []}
        
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            # Section header
            if stripped.startswith('[') and stripped.endswith(']'):
                section_name = stripped[1:-1].strip()
                if section_name == 'global':
                    current_section = 'global'
                elif section_name == 'accounts':
                    current_section = 'accounts'
                elif section_name.startswith('/'):
                    current_section = 'volume'
                    current_volume_path = section_name
                    parsed['volumes'].append({
                        'path': section_name, 
                        'source': '',
                        'accs': {},
                        'flags': []
                    })
                i += 1
                continue
            
            # Handle inline comments
            if '  #' in stripped:
                stripped = stripped.split('  #')[0].strip()
            
            # Check if this is just a path (volume source) - for volume sections
            if current_section == 'volume' and parsed['volumes']:
                # Check if line looks like a filesystem path
                is_path = False
                test_str = stripped
                
                # Windows path with drive letter: must be LETTER:/ or LETTER:\
                # e.g., D:/Archivos or C:\Users\...
                if len(test_str) >= 3 and test_str[0].isalpha() and test_str[1] == ':' and test_str[2] in '/\\':
                    is_path = True
                # Unix absolute path (but not sections like [/path])
                elif test_str.startswith('/') and len(test_str) > 1 and test_str[1] != '/':
                    is_path = True
                # Relative path
                elif test_str.startswith('./') or test_str.startswith('..'):
                    is_path = True
                # Home directory
                elif test_str.startswith('~/'):
                    is_path = True
                
                if is_path and not parsed['volumes'][-1]['source']:
                    # Remove inline comment if present
                    if '#' in test_str:
                        test_str = test_str.split('#')[0].strip()
                    parsed['volumes'][-1]['source'] = test_str
                    i += 1
                    continue
            
            # Key-value pair
            if ':' in stripped:
                # Split on first colon only
                colon_idx = stripped.index(':')
                key = stripped[:colon_idx].strip()
                value = stripped[colon_idx+1:].strip()
                
                if current_section == 'global':
                    # Handle flags without values (like e2dsa, e2ts, z, qr)
                    if not value and not key.startswith('-'):
                        # This might be a comma-separated list of flags
                        for flag in key.replace(',', ' ').split():
                            flag = flag.strip()
                            if flag:
                                parsed['global'][flag] = True
                    else:
                        parsed['global'][key] = value
                elif current_section == 'accounts':
                    parsed['accounts'][key] = value
                elif current_section == 'volume' and parsed['volumes']:
                    if key == 'accs':
                        # Next lines will have the actual permissions
                        pass
                    elif key in ('r', 'w', 'rw', 'rwm', 'rwmd', 'a', 'g', 'G', 'wG'):
                        # This is a permission line
                        parsed['volumes'][-1]['accs'][key] = value
                    elif key == 'flags':
                        # Next lines or value contains flags
                        if value:
                            parsed['volumes'][-1]['flags'].extend(
                                [f.strip() for f in value.replace(',', ' ').split() if f.strip()]
                            )
                    else:
                        # Check if it's a flag
                        if value:
                            parsed['volumes'][-1]['flags'].append(f'{key}={value}')
                        else:
                            parsed['volumes'][-1]['flags'].append(key)
            else:
                # Line without colon - could be flags or a path
                if current_section == 'global':
                    # Handle comma-separated flags
                    for flag in stripped.replace(',', ' ').split():
                        flag = flag.strip()
                        if flag:
                            parsed['global'][flag] = True
                elif current_section == 'volume' and parsed['volumes']:
                    # Could be flags
                    for flag in stripped.replace(',', ' ').split():
                        flag = flag.strip()
                        if flag:
                            parsed['volumes'][-1]['flags'].append(flag)
            
            i += 1
        
        # Apply parsed values to config
        if 'p' in parsed['global']:
            try:
                config['port'] = int(parsed['global']['p'].split(',')[0].strip())
            except:
                pass
        
        if 'i' in parsed['global']:
            config['interface'] = parsed['global']['i']
        
        if 'start_hidden' in parsed['global']:
            config['start_hidden'] = parsed['global']['start_hidden'].lower() in ('true', 'yes', '1')
        
        if 'theme' in parsed['global']:
            config['theme'] = parsed['global']['theme']
        
        config['accounts'] = parsed['accounts']
        config['volumes'] = parsed['volumes']
        config['_parsed'] = parsed
        
        return config
        
    except Exception as e:
        print(f"[CloudParty] Error loading config: {e}")
        return None


def create_example_config():
    """Create an example configuration file."""
    example_content = '''# CloudParty Configuration File
# Copy this file to cloudparty.conf and modify as needed
# -*- mode: yaml -*-

# ============================================================
# GLOBAL SETTINGS
# ============================================================
[global]
  # Port(s) to listen on (comma-separated for multiple)
  p: 3923
  
  # Interface to bind to (:: = all IPv4/IPv6, 0.0.0.0 = all IPv4)
  i: ::
  
  # Start with console hidden (tray app mode)
  start_hidden: true
  
  # Theme: cloudparty (dark blue/black), light, dark
  theme: cloudparty
  
  # Enable file indexing and scanning
  e2dsa
  
  # Enable multimedia indexing
  e2ts
  
  # Enable zeroconf and QR code
  z, qr

# ============================================================
# ACCOUNTS
# Define users with username: password format
# ============================================================
[accounts]
  admin: admin123
  guest: guest

# ============================================================
# VOLUMES
# Define shared folders with access permissions
# Format: [/mount_path] followed by settings
# ============================================================

# Root volume - main shared folder
[/]
  D:/Archivos
  accs:
    r: *         # Everyone can read
    rw: admin    # Admin can read/write

# Example: Private folder only for admin
[/private]
  D:/Private
  accs:
    rw: admin

# Example: Public upload folder
[/uploads]
  D:/Uploads
  accs:
    w: *         # Everyone can write/upload
    rw: admin    # Admin can read/write
  flags:
    e2d          # Enable uploads database
    nodupe       # Reject duplicate uploads

# ============================================================
# NOTES
# ============================================================
# 
# Permission types:
#   r  = read (list folders, download files)
#   w  = write (upload files)
#   rw = read + write
#   m  = move files/folders
#   d  = delete files/folders
#   a  = admin access
#   *  = everyone (including anonymous)
#
# To run CloudParty:
# 1. Copy this file to cloudparty.conf
# 2. Modify the settings above
# 3. Double-click cloudparty.exe
#
# The tray icon will appear. Right-click for options:
# - Show/Hide Console
# - Open in Browser
# - Reload Config
# - Exit
'''
    
    try:
        with open(EXAMPLE_CONFIG, 'w', encoding='utf-8') as f:
            f.write(example_content)
        print(f"[CloudParty] Example config created: {EXAMPLE_CONFIG}")
    except Exception as e:
        print(f"[CloudParty] Error creating example config: {e}")


def build_args_from_config(config):
    """Build command-line arguments from configuration."""
    args = []
    
    parsed = config.get('_parsed', {})
    
    # Port
    if 'p' in parsed.get('global', {}):
        args.extend(['-p', parsed['global']['p']])
    
    # Interface
    if 'i' in parsed.get('global', {}):
        args.extend(['-i', parsed['global']['i']])
    
    # Accounts
    for user, password in config.get('accounts', {}).items():
        args.extend(['-a', f'{user}:{password}'])
    
    # Volumes - format: source:mount:perm1:perm2:...
    # Example: D:/Archivos:archivos:r,*:rw,admin
    for vol in config.get('volumes', []):
        mount_path = vol.get('path', '/')
        source_dir = vol.get('source', '')
        accs = vol.get('accs', {})
        flags = vol.get('flags', [])
        
        if not source_dir:
            print(f"[CloudParty] Warning: Volume {mount_path} has no source directory, skipping")
            continue
        
        # Normalize source path (use forward slashes)
        source_dir = source_dir.replace('\\', '/')
        
        # Build permission parts: perm,user format
        accs_parts = []
        for perm, users in accs.items():
            # users can be "*" or "admin" or "user1 user2"
            for user in users.split():
                user = user.strip()
                if user:
                    accs_parts.append(f'{perm},{user}')
        
        # Build volume argument: source:mount:perm1:perm2:...
        # Mount path needs to be the web path (e.g., archivos for /archivos)
        mount_name = mount_path.lstrip('/') if mount_path != '/' else ''
        
        # Start with source and mount
        vol_parts = [source_dir, mount_name]
        
        # Add permissions
        vol_parts.extend(accs_parts)
        
        # Add flags if any (c,flag1,flag2 format)
        if flags:
            vol_parts.append('c,' + ','.join(flags))
        
        vol_arg = ':'.join(vol_parts)
        args.extend(['-v', vol_arg])
    
    # Theme argument - copyparty uses numeric themes (0-9)
    # We use theme 6 (hacker dark) as base and add custom CSS
    theme = config.get('theme', 'cloudparty')
    if theme == 'cloudparty':
        # Use dark theme as base (theme 6 = hacker dark is closest to our style)
        args.extend(['--theme', '6'])
        # Add custom CSS file if it exists
        css_file = APP_DIR / "copyparty" / "web" / "cloudparty.css"
        if not css_file.exists():
            css_file = APP_DIR / "cloudparty.css"
        if css_file.exists():
            args.extend(['--css-browser', str(css_file)])
    elif theme.isdigit():
        args.extend(['--theme', theme])
    
    # Extra global flags
    global_cfg = parsed.get('global', {})
    # Map config flags to copyparty argument names
    # Note: e2dsa and e2ts use single dash in copyparty
    flag_mapping = {
        'e2dsa': '-e2dsa',   # Single dash!
        'e2ts': '-e2ts',     # Single dash!
        'z': '--zs',         # zeroconf service
        'qr': '--qr',
    }
    for key, arg in flag_mapping.items():
        if key in global_cfg:
            args.append(arg)
    
    return args


class CloudPartyTray:
    """System tray application for CloudParty."""
    
    def __init__(self):
        self.config = None
        self.copyparty_thread = None
        self._console_visible = True
        self._console_lock = threading.Lock()
        self.icon = None
        self.copyparty_args = []
        self.warnings = []  # Store warnings for display
        
    @property
    def console_visible(self):
        with self._console_lock:
            return self._console_visible
    
    @console_visible.setter
    def console_visible(self, value):
        with self._console_lock:
            self._console_visible = value
        
    def create_icon_image(self):
        """Load the icon image from file or create a fallback."""
        if not HAVE_PIL:
            return None
            
        try:
            from PIL import Image
            
            # Try to load the custom icon file
            icon_paths = [
                APP_DIR / "cloudparty.ico",
                APP_DIR / "app-icon.ico", 
                APP_DIR / "app-icon.png",
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    try:
                        img = Image.open(str(icon_path))
                        # Resize to 64x64 for tray icon
                        img = img.resize((64, 64), Image.Resampling.LANCZOS)
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        return img
                    except Exception as e:
                        print(f"[CloudParty] Could not load icon {icon_path}: {e}")
                        continue
            
            # Fallback: create a simple icon programmatically
            from PIL import ImageDraw
            
            size = 64
            img = Image.new('RGBA', (size, size), (10, 25, 41, 255))  # #0a1929
            draw = ImageDraw.Draw(img)
            
            # Draw a cloud shape (simplified)
            draw.ellipse([8, 24, 40, 48], fill=(30, 58, 95, 255))
            draw.ellipse([24, 16, 56, 48], fill=(30, 58, 95, 255))
            draw.ellipse([16, 28, 48, 52], fill=(30, 58, 95, 255))
            
            # Highlight
            draw.ellipse([12, 26, 36, 44], fill=(66, 165, 245, 255))
            draw.ellipse([28, 20, 52, 44], fill=(66, 165, 245, 255))
            
            # Arrow pointing up
            draw.polygon([(32, 36), (24, 48), (40, 48)], fill=(255, 255, 255, 255))
            draw.rectangle([28, 44, 36, 56], fill=(255, 255, 255, 255))
            
            return img
            
        except Exception as e:
            print(f"[CloudParty] Error creating icon: {e}")
            return None
    
    def on_show_console(self, icon=None, item=None):
        """Toggle console visibility."""
        if self.console_visible:
            hide_console()
            self.console_visible = False
        else:
            show_console()
            self.console_visible = True
        self.update_menu()
    
    def on_open_browser(self, icon=None, item=None):
        """Open CloudParty in the default browser."""
        import webbrowser
        port = self.config.get('port', 3923) if self.config else 3923
        webbrowser.open(f'http://localhost:{port}/')
    
    def on_reload_config(self, icon=None, item=None):
        """Reload the configuration file."""
        print("[CloudParty] Reloading configuration...")
        self.config = load_config()
        if self.config:
            print("[CloudParty] Configuration reloaded successfully")
        else:
            print("[CloudParty] Failed to reload configuration")
    
    def on_exit(self, icon=None, item=None):
        """Exit the application."""
        print("[CloudParty] Shutting down...")
        set_running(False)
        # Show console before exit to display any final messages
        show_console()
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        # Give threads a moment to clean up
        time.sleep(0.5)
        os._exit(0)  # Force exit as copyparty might not respond to normal exit
    
    def update_menu(self):
        """Update the tray menu by recreating it."""
        if self.icon and HAVE_PYSTRAY:
            try:
                self.icon.menu = self.create_menu()
            except Exception as e:
                print(f"[CloudParty] Menu update error: {e}")
    
    def create_menu(self):
        """Create the tray menu."""
        if not HAVE_PYSTRAY:
            return None
            
        try:
            from pystray import MenuItem, Menu
            
            # Use a callable for dynamic text
            def get_console_text(item):
                return "Hide Console" if self.console_visible else "Show Console"
            
            return Menu(
                MenuItem(get_console_text, self.on_show_console),
                MenuItem("Open in Browser", self.on_open_browser),
                MenuItem("Reload Config", self.on_reload_config),
                MenuItem("---", None, enabled=False),  # Separator alternative
                MenuItem("Exit", self.on_exit)
            )
        except Exception as e:
            print(f"[CloudParty] Menu creation error: {e}")
            return None
    
    def run_copyparty(self):
        """Run the copyparty server."""
        try:
            # Import copyparty main
            from copyparty.__main__ import main as copyparty_main
            
            # Create a copy of argv for this thread to avoid race conditions
            copyparty_argv = ['cloudparty'] + list(self.copyparty_args)
            
            # Temporarily replace sys.argv
            import copy
            original_argv = copy.copy(sys.argv)
            sys.argv = copyparty_argv
            
            try:
                copyparty_main()
            except SystemExit as e:
                if e.code != 0:
                    print(f"[CloudParty] copyparty exited with code {e.code}")
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            print(f"[CloudParty] Error running copyparty: {e}")
            import traceback
            traceback.print_exc()
            # Show console so user can see the error
            show_console()
            self.console_visible = True
    
    def run_tray(self):
        """Run the system tray icon."""
        if not HAVE_PYSTRAY or not HAVE_PIL:
            print("[CloudParty] pystray or PIL not available")
            print("[CloudParty] Running without tray icon...")
            print("[CloudParty] Press Ctrl+C to exit")
            show_console()  # Make sure console is visible if no tray
            self.console_visible = True
            try:
                while is_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[CloudParty] Interrupted")
            return
            
        try:
            from PIL import Image
            
            icon_image = self.create_icon_image()
            if icon_image is None:
                icon_image = Image.new('RGBA', (64, 64), (30, 58, 95, 255))
            
            self.icon = pystray.Icon(
                "CloudParty",
                icon_image,
                "CloudParty File Server",
                menu=self.create_menu()
            )
            
            self.icon.run()
            
        except Exception as e:
            print(f"[CloudParty] Tray error: {e}")
            import traceback
            traceback.print_exc()
            show_console()  # Show console if tray fails
            self.console_visible = True
            try:
                while is_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[CloudParty] Interrupted")
    
    def run(self):
        """Main entry point."""
        # Set up console handler to intercept close button
        setup_console_handler()
        
        print("=" * 60)
        print("  CloudParty - File Sharing Server")
        print("=" * 60)
        print()
        
        # Check dependencies
        if not HAVE_PYSTRAY:
            print("[CloudParty] Note: pystray not installed - no tray icon")
            print("             Install with: pip install pystray")
        if not HAVE_PIL:
            print("[CloudParty] Note: PIL not installed - no tray icon")
            print("             Install with: pip install pillow")
        
        # Load configuration
        self.config = load_config()
        
        if self.config is None:
            print()
            print("[CloudParty] No configuration found!")
            print(f"[CloudParty] Please copy {EXAMPLE_CONFIG.name} to {CONFIG_FILE.name}")
            print("[CloudParty] and modify it according to your needs.")
            print()
            # Check if we have a TTY before waiting for input
            if sys.stdin.isatty():
                print("Press Enter to exit...")
                try:
                    input()
                except EOFError:
                    pass
            return
        
        print(f"[CloudParty] Configuration loaded from: {CONFIG_FILE}")
        
        # Build arguments
        self.copyparty_args = build_args_from_config(self.config)
        print(f"[CloudParty] Arguments: {' '.join(self.copyparty_args)}")
        
        # Print any warnings
        for warning in self.warnings:
            print(f"[CloudParty] Warning: {warning}")
        
        set_running(True)
        
        # Hide console if configured (and tray is available)
        if self.config.get('start_hidden', True) and HAVE_PYSTRAY and HAVE_PIL:
            print("[CloudParty] Hiding console in 2 seconds (right-click tray icon to show)")
            print()
            time.sleep(2)
            hide_console()
            self.console_visible = False
        else:
            print()
        
        # Start copyparty in a separate thread
        self.copyparty_thread = threading.Thread(target=self.run_copyparty, daemon=True)
        self.copyparty_thread.start()
        
        # Give copyparty a moment to start
        time.sleep(1)
        
        # Run tray icon (blocks until exit)
        self.run_tray()


def main():
    """Main entry point."""
    tray = CloudPartyTray()
    tray.run()


if __name__ == "__main__":
    main()
