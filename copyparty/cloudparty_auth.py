# coding: utf-8
"""
CloudParty Authentication Utilities
Provides password hashing compatible with copyparty's native system
"""
from __future__ import print_function, unicode_literals

import os
import sys
import base64

# Check for argon2 availability
try:
    if os.environ.get("PRTY_NO_ARGON2"):
        raise Exception()

    from argon2.low_level import hash_secret, Type as ArgonType
    HAVE_ARGON2 = True
except:
    HAVE_ARGON2 = False


def _get_copyparty_config_dir():
    """Get the copyparty config directory path."""
    # Check XDG_CONFIG_HOME first
    p = os.environ.get("XDG_CONFIG_HOME")
    if p and not p.startswith("~"):
        p = os.path.join(p, "copyparty")
        if os.path.isdir(p):
            return p

    # Windows: use APPDATA
    if sys.platform == "win32":
        bdir = os.environ.get("APPDATA") or os.environ.get("TEMP") or "."
        return os.path.normpath(bdir + "/copyparty")

    # macOS
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Preferences/copyparty")

    # Linux/Unix: use ~/.config/copyparty
    return os.path.expanduser("~/.config/copyparty")


def _get_ah_salt():
    """
    Get the password hashing salt used by copyparty.
    Reads from the same file copyparty uses.
    """
    config_dir = _get_copyparty_config_dir()
    salt_file = os.path.join(config_dir, "ah-salt.txt")

    try:
        with open(salt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        # If salt file doesn't exist, create the directory and generate a new salt
        try:
            os.makedirs(config_dir, exist_ok=True)
            salt = base64.urlsafe_b64encode(os.urandom(18)).decode('utf-8')
            with open(salt_file, 'w', encoding='utf-8') as f:
                f.write(salt + '\n')
            return salt
        except Exception as e:
            print(f"[CloudParty Auth] Warning: Could not read/create salt file: {e}", file=sys.stderr)
            # Return a default salt (not ideal, but allows operation)
            return "cloudparty_default_salt"


def hash_password_copyparty(password):
    """
    Hash a password using copyparty's native argon2 format.

    This generates hashes compatible with copyparty's --ah-alg argon2 system.
    The hash starts with '+' and is exactly 33 characters long.

    Args:
        password: Plain text password

    Returns:
        Hashed password string in copyparty format (+XXXX...XXX, 33 chars)
    """
    if not HAVE_ARGON2:
        raise Exception("argon2 is required for password hashing")

    salt = _get_ah_salt().encode('utf-8')

    # Use the same parameters as copyparty's pwhash.py _gen_argon2
    # Default: time_cost=3, mem_cost=256 (MiB), parallelism=4, version=19
    time_cost = 3
    mem_cost = 256 * 1024  # 256 MiB in KiB
    parallelism = 4
    version = 19

    bplain = password.encode('utf-8')

    bret = hash_secret(
        secret=bplain,
        salt=salt,
        time_cost=time_cost,
        memory_cost=mem_cost,
        parallelism=parallelism,
        hash_len=24,
        type=ArgonType.ID,
        version=version,
    )

    # Extract just the hash part (after the last $)
    ret = bret.split(b"$")[-1].decode('utf-8')

    # Convert to copyparty format: replace / with _ and + with -
    ret = "+" + ret.replace("/", "_").replace("+", "-")

    return ret


def is_password_hashed(password):
    """
    Check if a password is already hashed in copyparty format.

    Copyparty hashes start with '+' and are exactly 33 characters.

    Args:
        password: Password string to check

    Returns:
        True if password appears to be hashed, False otherwise
    """
    if not password:
        return False

    # Copyparty format: starts with + and is 33 chars
    if password.startswith('+') and len(password) == 33:
        return True

    return False


def auto_hash_password(password):
    """
    Automatically hash a password if it's not already hashed.

    Args:
        password: Password string (plain or hashed)

    Returns:
        Hashed password in copyparty format (or original if already hashed)
    """
    if is_password_hashed(password):
        return password

    # Password is plain text, hash it
    return hash_password_copyparty(password)


def needs_first_time_setup(config):
    """
    Check if CloudParty needs first-time setup (no admin account).

    Args:
        config: Configuration dictionary

    Returns:
        True if setup needed, False otherwise
    """
    if not config:
        return True

    accounts = config.get('accounts', {})

    # No accounts at all = needs setup
    if not accounts:
        return True

    # Check for placeholder passwords that indicate setup needed
    for username, password in accounts.items():
        if username == 'admin':
            # Check for common placeholder passwords (plain text)
            placeholders = [
                'CHANGE_ME_IMMEDIATELY_USE_STRONG_PASSWORD',
                'CHANGE_THIS_ADMIN_PASSWORD_NOW',
                'CHANGE_THIS_PASSWORD',
                'change_me',
                'admin',
                'admin123',
                'password',
                '1234',
                '12345',
                '123456'
            ]

            if password in placeholders:
                return True

            # If admin exists with hashed or non-placeholder password, no setup needed
            return False

    # Admin account doesn't exist = needs setup
    return True


def generate_secure_random_password(length=20):
    """
    Generate a cryptographically secure random password.

    Args:
        length: Password length (default 20)

    Returns:
        Random password string
    """
    import string
    import secrets

    # Use all printable ASCII except confusing characters
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    # Remove confusing characters
    alphabet = alphabet.replace('0', '').replace('O', '').replace('l', '').replace('1', '').replace('I', '')

    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


# Aliases for backward compatibility
hash_password_argon2 = hash_password_copyparty


# Export main functions
__all__ = [
    'hash_password_copyparty',
    'hash_password_argon2',  # alias
    'is_password_hashed',
    'auto_hash_password',
    'needs_first_time_setup',
    'generate_secure_random_password',
    'HAVE_ARGON2'
]
