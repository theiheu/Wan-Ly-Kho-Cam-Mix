#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persistent Paths Manager for Quan Ly Kho Cam & Mix Manager
Handles data paths for professional Windows installation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def detect_execution_environment():
    """Detect if running from executable or development"""
    import sys

    # Check if running from PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return 'executable'

    # Check if main script is in expected development location
    main_file = Path(sys.argv[0]).resolve()
    if 'src' in main_file.parts:
        return 'development'

    return 'executable'

def is_installed_application():
    """Check if running as installed application (should use AppData)"""
    if not getattr(sys, 'frozen', False):
        return False

    exe_path = Path(sys.executable).resolve()

    # Check if installed in Program Files or similar system directories
    system_dirs = [
        Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
        Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
        Path(os.environ.get('PROGRAMW6432', 'C:\\Program Files'))
    ]

    for system_dir in system_dirs:
        try:
            if system_dir in exe_path.parents:
                return True
        except (OSError, ValueError):
            continue

    # Check for installation marker or registry entry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"Software\Quan_Ly_Kho_Cam_&_Mix\Quan_Ly_Kho_Cam_&_Mix")
        winreg.CloseKey(key)
        return True
    except (ImportError, FileNotFoundError, OSError):
        pass

    return False

class PersistentPathManager:
    """Manages persistent data paths for the application"""

    def __init__(self):
        self.execution_env = detect_execution_environment()
        self.is_installed = is_installed_application()

        if self.execution_env == 'executable':
            app_name = "Quan_Ly_Kho_Cam_&_Mix"

            if self.is_installed:
                # Always use AppData for installed applications
                base_path = Path(os.environ.get('APPDATA', '')) / app_name
                print(f"🔧 Installed application detected - using AppData: {base_path}")
            else:
                # Standalone executable - use AppData as well for consistency
                base_path = Path(os.environ.get('APPDATA', '')) / app_name
                print(f"🔧 Standalone executable - using AppData: {base_path}")
        else:
            # Development mode - use project structure
            base_path = Path(__file__).parent.parent / "data"
            print(f"🔧 Development mode - using project data: {base_path}")

        self.data_path = base_path
        self.config_path = base_path / "config"
        self.logs_path = base_path / "logs"
        self.reports_path = base_path / "reports"
        self.exports_path = base_path / "exports"
        self.backups_path = base_path / "backups"

        # Ensure all directories exist
        self._ensure_directories()

    def _detect_installation_mode(self) -> bool:
        """Detect if running in professional installation mode"""
        try:
            # Check for installation marker file
            marker_file = Path(__file__).parent.parent.parent / "installer" / "output" / ".installation_marker"
            if marker_file.exists():
                self._safe_print("Professional installation detected via marker file")
                return True

            # Check if running from installer/output directory
            current_path = Path(__file__).resolve()
            if "installer" in str(current_path) and "output" in str(current_path):
                self._safe_print("Professional installation detected via path analysis")
                return True

            # Check for environment variable
            if os.environ.get('CFM_INSTALLATION_MODE') == 'professional':
                self._safe_print("Professional installation detected via environment variable")
                return True

            # Check if data directories exist in expected professional locations
            potential_data_path = Path.home() / "AppData" / "Local" / "Quan_Ly_Kho_Cam_&_MixFeedManager" / "data"
            if potential_data_path.exists():
                self._safe_print("Professional installation detected via data directory")
                return True

            self._safe_print("Development mode detected")
            return False

        except Exception as e:
            self._safe_print(f"Error detecting installation mode: {e}")
            return False

    def _safe_print(self, message: str):
        """Safe print function that handles unicode encoding issues"""
        try:
            # Remove emoji characters for executable compatibility
            safe_message = message.replace("🏢", "[PROF]").replace("🔧", "[DEV]").replace("⚠️", "[WARN]").replace("🔍", "[INFO]")
            print(safe_message)
        except UnicodeEncodeError:
            # Fallback to ASCII-only message
            ascii_message = message.encode('ascii', 'ignore').decode('ascii')
            print(ascii_message)
        except Exception:
            # Ultimate fallback
            print("Installation mode detection message")

    def _get_fallback_data_path(self):
        """Get fallback data path"""

        if getattr(sys, 'frozen', False):
            # Get actual executable directory, NOT temp directory
            exe_dir = Path(sys.executable).parent

            print(f"🔍 Frozen mode - exe_dir: {exe_dir}")

            if self.is_professional_install:
                # Professional mode - use AppData
                appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
                data_path = appdata / self.app_name / "data"
                print(f"🔍 Professional data path: {data_path}")
                return data_path
            else:
                # Portable mode - use executable directory
                data_path = exe_dir / "data"
                print(f"🔍 Portable data path: {data_path}")
                return data_path
        else:
            # Development mode
            data_path = Path(__file__).parent.parent.parent / "src" / "data"
            print(f"🔍 Development data path: {data_path}")
            return data_path

    def _get_fallback_config_path(self):
        """Get fallback config path"""

        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent

            if self.is_professional_install:
                appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
                return appdata / self.app_name / "config"
            else:
                return exe_dir / "config"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "config"

    def _get_fallback_logs_path(self):
        """Get fallback logs path"""
        if self.is_professional_install:
            appdata = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
            return appdata / self.app_name / "logs"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "logs"

    def _get_fallback_reports_path(self):
        """Get fallback reports path"""

        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent

            if self.is_professional_install:
                documents = Path(os.environ.get('USERPROFILE', Path.home())) / 'Documents'
                return documents / self.app_name / "reports"
            else:
                return exe_dir / "reports"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "reports"

    def _get_fallback_exports_path(self):
        """Get fallback exports path"""

        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent

            if self.is_professional_install:
                documents = Path(os.environ.get('USERPROFILE', Path.home())) / 'Documents'
                return documents / self.app_name / "exports"
            else:
                return exe_dir / "exports"
        else:
            return Path(__file__).parent.parent.parent / "src" / "data" / "exports"

    def _get_fallback_backups_path(self):
        """Get fallback backups path"""
        if self.is_professional_install:
            documents = Path(os.environ.get('USERPROFILE', Path.home())) / 'Documents'
            return documents / self.app_name / "backups"
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
        old_data_dir = Path(__file__).parent.parent / "data"

        if not old_data_dir.exists():
            return

        print("🔄 Migrating data to persistent storage...")
        migration_log = []
        errors = []

        try:
            import shutil

            # Create migration mapping for all data types
            migration_mapping = {
                # Direct data files (JSON files in root data directory)
                "data_files": {
                    "source": old_data_dir,
                    "destination": self.data_path,
                    "patterns": ["*.json", "*.txt", "*.csv"]
                },
                # Config files
                "config": {
                    "source": old_data_dir / "config",
                    "destination": self.config_path,
                    "patterns": ["*"]
                },
                # Log files
                "logs": {
                    "source": old_data_dir / "logs",
                    "destination": self.logs_path,
                    "patterns": ["*"]
                },
                # Reports
                "reports": {
                    "source": old_data_dir / "reports",
                    "destination": self.reports_path,
                    "patterns": ["*"]
                },
                # Exports
                "exports": {
                    "source": old_data_dir / "exports",
                    "destination": self.exports_path,
                    "patterns": ["*"]
                },
                # Backups
                "backups": {
                    "source": old_data_dir / "backups",
                    "destination": self.backups_path,
                    "patterns": ["*"]
                },
                # Presets (special handling)
                "presets": {
                    "source": old_data_dir / "presets",
                    "destination": self.data_path / "presets",
                    "patterns": ["*"]
                }
            }

            # Migrate each category
            for category, mapping in migration_mapping.items():
                source_dir = mapping["source"]
                dest_dir = mapping["destination"]
                patterns = mapping["patterns"]

                if not source_dir.exists():
                    continue

                print(f"📁 Migrating {category}...")

                # Ensure destination directory exists
                dest_dir.mkdir(parents=True, exist_ok=True)

                if category == "data_files":
                    # Handle root data files
                    for pattern in patterns:
                        for file_path in source_dir.glob(pattern):
                            if file_path.is_file():
                                dest_path = dest_dir / file_path.name
                                if not dest_path.exists():
                                    try:
                                        shutil.copy2(file_path, dest_path)
                                        migration_log.append(f"✅ Migrated: {file_path.name}")
                                        print(f"  ✅ {file_path.name}")
                                    except Exception as e:
                                        error_msg = f"❌ Failed to migrate {file_path.name}: {e}"
                                        errors.append(error_msg)
                                        print(f"  {error_msg}")
                                else:
                                    print(f"  ⏭️ Skipped (exists): {file_path.name}")
                else:
                    # Handle subdirectories recursively
                    if source_dir.exists():
                        for file_path in source_dir.rglob("*"):
                            if file_path.is_file():
                                try:
                                    # Calculate relative path from source
                                    relative_path = file_path.relative_to(source_dir)
                                    dest_path = dest_dir / relative_path

                                    # Create parent directories if needed
                                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                                    # Copy file if it doesn't exist or is newer
                                    should_copy = False
                                    if not dest_path.exists():
                                        should_copy = True
                                    else:
                                        # Check if source is newer
                                        source_mtime = file_path.stat().st_mtime
                                        dest_mtime = dest_path.stat().st_mtime
                                        if source_mtime > dest_mtime:
                                            should_copy = True

                                    if should_copy:
                                        shutil.copy2(file_path, dest_path)
                                        migration_log.append(f"✅ Migrated: {category}/{relative_path}")
                                        print(f"  ✅ {relative_path}")
                                    else:
                                        print(f"  ⏭️ Skipped (up-to-date): {relative_path}")

                                except Exception as e:
                                    error_msg = f"❌ Failed to migrate {category}/{file_path.name}: {e}"
                                    errors.append(error_msg)
                                    print(f"  {error_msg}")

            # Create migration summary
            summary_file = self.data_path / "migration_log.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("Data Migration Log\n")
                f.write("==================\n")
                f.write(f"Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source: {old_data_dir}\n")
                f.write(f"Destination Base: {self.data_path.parent}\n\n")

                f.write("Successfully Migrated Files:\n")
                f.write("-" * 30 + "\n")
                for log_entry in migration_log:
                    f.write(f"{log_entry}\n")

                if errors:
                    f.write(f"\nErrors ({len(errors)}):\n")
                    f.write("-" * 15 + "\n")
                    for error in errors:
                        f.write(f"{error}\n")

                f.write(f"\nTotal Files Migrated: {len(migration_log)}\n")
                f.write(f"Total Errors: {len(errors)}\n")

            # Print summary
            print(f"\n📊 Migration Summary:")
            print(f"  ✅ Files migrated: {len(migration_log)}")
            print(f"  ❌ Errors: {len(errors)}")
            print(f"  📄 Log saved: {summary_file}")

            if errors:
                print(f"\n⚠️ Migration completed with {len(errors)} errors")
                print("Check migration_log.txt for details")
            else:
                print("✅ Migration completed successfully!")

        except Exception as e:
            error_msg = f"⚠️ Critical migration error: {e}"
            print(error_msg)

            # Save critical error log
            try:
                error_log = self.data_path / "migration_error.txt"
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write(f"Critical Migration Error\n")
                    f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Error: {e}\n")
                    f.write(f"Source Directory: {old_data_dir}\n")

                    import traceback
                    f.write(f"\nTraceback:\n{traceback.format_exc()}")
            except:
                pass

    def verify_migration(self):
        """Verify that migration was successful"""
        if not self.is_professional_install:
            return True

        print("🔍 Verifying migration...")

        # Check critical files exist
        critical_files = [
            self.get_config_file_path("feed_formula.json"),
            self.get_config_file_path("mix_formula.json"),
            self.get_config_file_path("inventory.json")
        ]

        missing_files = []
        for file_path in critical_files:
            if not file_path.exists():
                missing_files.append(file_path.name)

        if missing_files:
            print(f"⚠️ Missing critical files: {', '.join(missing_files)}")
            return False

        print("✅ Migration verification passed")
        return True

    def get_installation_info(self):
        """Get installation information"""
        return {
            "is_professional_install": self.is_professional_install,
            "data_path": str(self.data_path),
            "config_path": str(self.config_path),
            "logs_path": str(self.logs_path),
            "reports_path": str(self.reports_path),
            "exports_path": str(self.exports_path),
            "backups_path": str(self.backups_path),
            "migration_completed": (self.data_path / "migration_log.txt").exists()
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

    # Verify migration was successful
    if not persistent_path_manager.verify_migration():
        print("⚠️ Migration verification failed - initializing default data")
        # Initialize default data if migration failed
        try:
            from src.utils.init_data import init_data
            init_data()
        except ImportError:
            try:
                from utils.init_data import init_data
                init_data()
            except ImportError:
                print("⚠️ Could not initialize default data")

except Exception as e:
    print(f"Warning: Data migration failed: {e}")
    # Try to initialize default data as fallback
    try:
        from src.utils.init_data import init_data
        init_data()
    except ImportError:
        try:
            from utils.init_data import init_data
            init_data()
        except ImportError:
            print("⚠️ Could not initialize fallback data")















