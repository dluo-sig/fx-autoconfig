#!/usr/bin/env python3
"""Test script to verify startup cache path logic"""

import os
import platform
from pathlib import Path

def get_startup_cache_path(profile_path):
    """Get the correct startup cache path for the current platform"""
    if not profile_path:
        return None
    
    system = platform.system()
    
    if system == "Windows":
        # On Windows, startup cache is in Local AppData, not Roaming
        profile_name = os.path.basename(profile_path)
        cache_dir = os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            "Mozilla", "Firefox", "Profiles", profile_name, "startupCache"
        )
    else:
        # On macOS and Linux, startup cache is in the profile directory
        cache_dir = os.path.join(profile_path, "startupCache")
    
    return cache_dir

if __name__ == "__main__":
    # Test with a sample profile path
    if platform.system() == "Windows":
        sample_profile = r"C:\Users\TestUser\AppData\Roaming\Mozilla\Firefox\Profiles\abc123.default-release"
        expected_cache = os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            "Mozilla", "Firefox", "Profiles", "abc123.default-release", "startupCache"
        )
    else:
        sample_profile = "/home/testuser/.mozilla/firefox/abc123.default-release"
        expected_cache = "/home/testuser/.mozilla/firefox/abc123.default-release/startupCache"
    
    actual_cache = get_startup_cache_path(sample_profile)
    
    print(f"Platform: {platform.system()}")
    print(f"Sample profile: {sample_profile}")
    print(f"Expected cache: {expected_cache}")
    print(f"Actual cache: {actual_cache}")
    print(f"Match: {actual_cache == expected_cache}")
    
    if platform.system() == "Windows":
        print(f"LOCALAPPDATA: {os.environ.get('LOCALAPPDATA', 'NOT SET')}")
        print(f"APPDATA: {os.environ.get('APPDATA', 'NOT SET')}")
