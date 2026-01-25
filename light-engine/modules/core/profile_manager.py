import os
import shutil
import zipfile
import platform
from pathlib import Path
import json

class ChromeProfileManager:
    """Manage Chrome profile data transfer between PCs"""
    
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
    
    def export_profile(self, profile_name="Default", output_path="chrome_profile_backup.zip", include_parent_files=True):
        """
        Export Chrome profile to a zip file (recursively searches all nested folders)
        
        Args:
            profile_name: Name of the Chrome profile (usually "Default" or "Profile 1", etc.)
            output_path: Path where the zip file will be saved
            include_parent_files: If True, also exports parent User Data files (Local State, etc.)
        """
        profile_path = self.chrome_data_path / profile_name
        
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile not found at: {profile_path}")
        
        # WHITELIST approach - only skip these directories (everything else is included)
        skip_dirs = {
            'Cache', 'cache',
            'Code Cache',
            'GPUCache', 'GpuCache',
            'Service Worker', 'ServiceWorker',
            'ShaderCache',
            'DawnCache',
            'DawnGraphiteCache',
            'DawnWebGPUCache',
            'GrShaderCache',
            'blob_storage',
            'VideoDecodeStats',
            'BudgetDatabase',
            'optimization_guide_hint_cache_store',
            'optimization_guide_model_and_features_store',
            'LOG', 'LOG.old',  # Log files
        }
        
        # Files to skip (by exact name)
        skip_files = {
            'LOCK',
            'lockfile',
            '.DS_Store',
            'Thumbs.db',
        }
        
        # Extensions to skip
        skip_extensions = {
            '.tmp', '.temp', '.log', '.dmp', '.etl', '.pma'
        }
        
        print(f"Creating backup of profile: {profile_name}")
        print(f"Scanning: {profile_path}\n")
        
        files_added = 0
        
        # Create zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # First, add parent User Data files if requested (needed for Playwright)
            if include_parent_files:
                print("Adding parent User Data files...")
                for item in self.chrome_data_path.iterdir():
                    if item.is_file():
                        # Include all files in User Data root
                        try:
                            zipf.write(item, arcname=f"_parent/{item.name}")
                            files_added += 1
                            print(f"  Added parent file: {item.name}")
                        except Exception as e:
                            print(f"  Skipped (error): {item.name} - {e}")
                print()
            
            # Walk through entire profile directory recursively
            print(f"Adding profile files from: {profile_name}")
            for root, dirs, files in os.walk(profile_path):
                root_path = Path(root)
                
                # Filter out skip directories IN-PLACE
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                relative_root = root_path.relative_to(profile_path)
                
                for file in files:
                    # Skip specific files
                    if file in skip_files:
                        continue
                    
                    # Skip by extension
                    file_ext = Path(file).suffix.lower()
                    if file_ext in skip_extensions:
                        continue
                    
                    file_path = root_path / file
                    
                    # Create archive name maintaining directory structure
                    if relative_root == Path('.'):
                        arc_name = f"{profile_name}/{file}"
                    else:
                        arc_name = f"{profile_name}/{relative_root}/{file}"
                    
                    try:
                        zipf.write(file_path, arcname=arc_name)
                        files_added += 1
                        
                        # Only print every 50th file to avoid spam
                        if files_added % 50 == 0:
                            print(f"  Added {files_added} files so far...")
                    except Exception as e:
                        print(f"  Skipped (error): {arc_name} - {e}")
        
        # Store metadata
        metadata = {
            'profile_name': profile_name,
            'source_os': self.system,
            'chrome_version': self._get_chrome_version(),
            'files_count': files_added,
            'includes_parent_files': include_parent_files
        }
        
        # Add metadata to zip
        with zipfile.ZipFile(output_path, 'a') as zipf:
            zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
        
        print(f"\nProfile exported successfully to: {output_path}")
        print(f"Total files: {files_added}")
        print(f"Size: {Path(output_path).stat().st_size / (1024*1024):.2f} MB")
        return output_path
    
    def import_profile(self, zip_path, profile_name="Default", overwrite=False):
        """
        Import Chrome profile from a zip file to a custom directory (maintains nested folder structure)
        
        Args:
            zip_path: Path to the backup zip file
            target_dir: Target directory where profile will be extracted (will be used as user_data_dir)
            profile_name: Target profile name (usually "Default")
            overwrite: If True, overwrites existing files; if False, skips existing files
        """
        if not Path(zip_path).exists():
            raise FileNotFoundError(f"Backup file not found: {zip_path}")
        
        target_path = self._get_chrome_data_path()
        profile_path = target_path / profile_name
        
        # Create directories
        target_path.mkdir(parents=True, exist_ok=True)
        profile_path.mkdir(parents=True, exist_ok=True)
        
        print(f"Importing profile to: {target_path}")
        print(f"Profile folder: {profile_name}\n")
        
        # Read metadata
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            if 'metadata.json' in zipf.namelist():
                metadata = json.loads(zipf.read('metadata.json'))
                print(f"Source OS: {metadata.get('source_os', 'Unknown')}")
                print(f"Chrome Version: {metadata.get('chrome_version', 'Unknown')}")
                print(f"Total files in backup: {metadata.get('files_count', 'Unknown')}")
                print(f"Includes parent files: {metadata.get('includes_parent_files', False)}\n")
        
        # Extract files maintaining nested structure
        extracted_count = 0
        skipped_count = 0
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for file_info in zipf.filelist:
                # Skip metadata file
                if file_info.filename == 'metadata.json':
                    continue
                
                # Skip directories (they'll be created automatically)
                if file_info.is_dir():
                    continue
                
                parts = Path(file_info.filename).parts
                
                # Handle parent files (stored in _parent folder)
                if parts[0] == '_parent':
                    if len(parts) > 1:
                        target_file = target_path / parts[1]
                    else:
                        continue
                # Handle profile files
                elif len(parts) > 1:
                    # Reconstruct the full nested path
                    relative_path = Path(*parts[1:])
                    target_file = profile_path / relative_path
                else:
                    continue
                
                # Check if file exists
                if target_file.exists() and not overwrite:
                    skipped_count += 1
                    continue
                
                # Create all parent directories maintaining nested structure
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract file
                try:
                    with zipf.open(file_info) as source, open(target_file, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    extracted_count += 1
                    # Show relative path for better visibility
                    display_path = target_file.relative_to(target_path)
                    print(f"  Extracted: {display_path}")
                except Exception as e:
                    print(f"  Error extracting {file_info.filename}: {e}")
                    skipped_count += 1
        
        print(f"\nImport complete!")
        print(f"Files extracted: {extracted_count}")
        print(f"Files skipped: {skipped_count}")
        print(f"\nTo use with Playwright:")
        print(f"  user_data_dir=r'{target_path}'")
        
        return target_path

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