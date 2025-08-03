#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistent Paths Manager for Chicken Farm Manager
Handles data paths for professional Windows installation
"""

import os
import sys
from pathlib import Path

class PersistentPathManager:
    """Manages persistent data paths for the application"""
    
    def __init__(self):
        self.app_name = "ChickenFarmManager"
        
        # Check if running in professional installation mode
        self.is_professional_install = self._check_professional_install()
        
        if self.is_professional_install:
            # Use environment variables set by installation manager
            self.data_path = Path(os.environ.get('CFM_DATA_PATH', self._get_fallback_data_path()))
            self.config_path = Path(os.environ.get('CFM_CONFIG_PATH', self._get_fallback_config_path()))
            self.logs_path = Path(os.environ.get('CFM_LOGS_PATH', self._get_fallback_logs_path()))
            self.reports_path = Path(os.environ.get('CFM_REPORTS_PATH', self._get_fallback_reports_path()))
            self.exports_path = Path(os.environ.get('CFM_EXPORTS_PATH', self._get_fallback_exports_path()))
            self.backups_path = Path(os.environ.get('CFM_BACKUPS_PATH', self._get_fallback_backups_path()))
        else:
            # Fallback to relative paths for development/portable mode
            self.data_path = self._get_fallback_data_path()
            self.config_path = self._get_fallback_config_path()
            self.logs_path = self._get_fallback_logs_path()
            self.reports_path = self._get_fallback_reports_path()
            self.exports_path = self._get_fallback_exports_path()
            self.backups_path = self._get_fallback_backups_path()
        
        # Ensure all directories exist
        self._ensure_directories()

    def _check_professional_install(self):
        """Check if running in professional installation mode"""
        return 'CFM_DATA_PATH' in os.environ

    def _get_fallback_data_path(self):
        """Get fallback data path for development/portable mode"""
        if self.is_professional_install:
            return Path(os.environ.get('APPDATA', '')) / self.app_name / "data"
        else:
            # Use relative path for development
            return Path(__file__).parent.parent.parent / "src" / "data"

    def _get_fallback_config_path(self):
        """Get fallback config path"""
        if self.is_professional_install:
            return Path(os.environ.get('APPDATA', '')) / self.app_name / "config"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "config"

    def _get_fallback_logs_path(self):
        """Get fallback logs path"""
        if self.is_professional_install:
            return Path(os.environ.get('APPDATA', '')) / self.app_name / "logs"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "logs"

    def _get_fallback_reports_path(self):
        """Get fallback reports path"""
        if self.is_professional_install:
            return Path(os.environ.get('USERPROFILE', '')) / 'Documents' / self.app_name / "reports"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "reports"

    def _get_fallback_exports_path(self):
        """Get fallback exports path"""
        if self.is_professional_install:
            return Path(os.environ.get('USERPROFILE', '')) / 'Documents' / self.app_name / "exports"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "exports"

    def _get_fallback_backups_path(self):
        """Get fallback backups path"""
        if self.is_professional_install:
            return Path(os.environ.get('USERPROFILE', '')) / 'Documents' / self.app_name / "backups"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "backups"

    def _ensure_directories(self):
        """Ensure all directories exist"""
        directories = [
            self.data_path,
            self.config_path,
            self.logs_path,
            self.reports_path,
            self.exports_path,
            self.backups_path
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not create directory {directory}: {e}")

    def get_data_file_path(self, filename):
        """Get full path for a data file"""
        return self.data_path / filename

    def get_config_file_path(self, filename):
        """Get full path for a config file"""
        return self.config_path / filename

    def get_log_file_path(self, filename):
        """Get full path for a log file"""
        return self.logs_path / filename

    def get_report_file_path(self, filename):
        """Get full path for a report file"""
        return self.reports_path / filename

    def get_export_file_path(self, filename):
        """Get full path for an export file"""
        return self.exports_path / filename

    def get_backup_file_path(self, filename):
        """Get full path for a backup file"""
        return self.backups_path / filename

    def migrate_data_from_relative_paths(self):
        """Migrate data from old relative paths to new persistent paths"""
        if not self.is_professional_install:
            return  # No migration needed for development mode
        
        # Old relative data directory
        old_data_dir = Path(__file__).parent.parent.parent / "src" / "data"
        
        if not old_data_dir.exists():
            return
        
        print("🔄 Migrating data to persistent storage...")
        
        try:
            # Migrate data files
            for file_path in old_data_dir.glob("*.json"):
                dest_path = self.get_data_file_path(file_path.name)
                if not dest_path.exists():
                    import shutil
                    shutil.copy2(file_path, dest_path)
                    print(f"✅ Migrated: {file_path.name}")
            
            # Migrate subdirectories
            for subdir in ["config", "logs", "reports", "exports", "backups"]:
                old_subdir = old_data_dir / subdir
                if old_subdir.exists():
                    new_subdir = getattr(self, f"{subdir}_path")
                    for file_path in old_subdir.rglob("*"):
                        if file_path.is_file():
                            relative_path = file_path.relative_to(old_subdir)
                            dest_path = new_subdir / relative_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            if not dest_path.exists():
                                import shutil
                                shutil.copy2(file_path, dest_path)
                                print(f"✅ Migrated: {subdir}/{relative_path}")
        
        except Exception as e:
            print(f"⚠️ Data migration warning: {e}")

    def get_installation_info(self):
        """Get installation information"""
        return {
            "is_professional_install": self.is_professional_install,
            "data_path": str(self.data_path),
            "config_path": str(self.config_path),
            "logs_path": str(self.logs_path),
            "reports_path": str(self.reports_path),
            "exports_path": str(self.exports_path),
            "backups_path": str(self.backups_path)
        }

# Global instance
persistent_path_manager = PersistentPathManager()

# Convenience functions for backward compatibility
def get_data_path():
    """Get the main data directory path"""
    return persistent_path_manager.data_path

def get_data_file_path(filename):
    """Get full path for a data file"""
    return persistent_path_manager.get_data_file_path(filename)

def get_config_file_path(filename):
    """Get full path for a config file"""
    return persistent_path_manager.get_config_file_path(filename)

def get_report_file_path(filename):
    """Get full path for a report file"""
    return persistent_path_manager.get_report_file_path(filename)

def get_export_file_path(filename):
    """Get full path for an export file"""
    return persistent_path_manager.get_export_file_path(filename)

def get_backup_file_path(filename):
    """Get full path for a backup file"""
    return persistent_path_manager.get_backup_file_path(filename)

# Initialize data migration on import
try:
    persistent_path_manager.migrate_data_from_relative_paths()
except Exception as e:
    print(f"Warning: Data migration failed: {e}")
