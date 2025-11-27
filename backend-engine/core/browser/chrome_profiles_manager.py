import os
import platform
from pathlib import Path
import json

class ChromeProfileManager:
    """Manage Chrome profiles"""
    
    def __init__(self):
        self.system = platform.system()
        self.chrome_data_path = self._get_chrome_data_path()
    
    def _get_chrome_data_path(self):
        """Get Chrome user data path based on OS"""
        if self.system == "Windows":
            return Path(os.environ['LOCALAPPDATA']) / 'Google' / 'Chrome' / 'User Data'
        elif self.system == "Darwin":  # macOS
            return Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome'
        elif self.system == "Linux":
            return Path.home() / '.config' / 'google-chrome'
        else:
            raise OSError(f"Unsupported operating system: {self.system}")

    def _get_chrome_version(self):
        """Get Chrome version if available"""
        try:
            # Try to read from preferences
            prefs_path = self.chrome_data_path / 'Default' / 'Preferences'
            if prefs_path.exists():
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    return prefs.get('extensions', {}).get('last_chrome_version', 'Unknown')
        except:
            pass
        return 'Unknown'
    
    def list_profiles(self):
        """List all available Chrome profiles"""
        if not self.chrome_data_path.exists():
            print(f"Chrome data path not found: {self.chrome_data_path}")
            return []
        
        profiles = []
        for item in self.chrome_data_path.iterdir():
            if item.is_dir() and (item.name == "Default" or item.name.startswith("Profile")):
                profiles.append(item.name)
        
        return profiles