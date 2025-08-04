#!/usr/bin/env python3
"""
Code Signing Preparation Script for Windows Installers
Prepares installers for code signing with digital certificates
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
import json

class CodeSigningManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.installer_dir = self.project_root / "installer"
        self.output_dir = self.installer_dir / "output"
        self.scripts_dir = self.installer_dir / "scripts"

        # Code signing configuration
        self.signing_config = {
            "certificate_path": "",
            "certificate_password": "",
            "timestamp_url": "http://timestamp.digicert.com",
            "description": "Phần mềm Quản lý Cám - Trại Gà",
            "url": "https://github.com/Minh-Tan_Phat"
        }

    def check_signing_tools(self):
        """Check if code signing tools are available"""
        tools_status = {
            "signtool": False,
            "osslsigncode": False
        }

        # Check Windows SDK signtool
        signtool_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x86\signtool.exe",
            r"C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\signtool.exe"
        ]

        for path in signtool_paths:
            if Path(path).exists():
                tools_status["signtool"] = True
                self.signtool_path = path
                print(f"✅ SignTool found: {path}")
                break

        if not tools_status["signtool"]:
            print("⚠️ SignTool not found. Install Windows SDK for code signing.")

        # Check osslsigncode (alternative)
        try:
            subprocess.run(["osslsigncode", "--version"],
                          capture_output=True, text=True, check=True)
            tools_status["osslsigncode"] = True
            print("✅ osslsigncode available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ osslsigncode not found (alternative signing tool)")

        return tools_status

    def load_signing_config(self):
        """Load code signing configuration from file"""
        config_file = self.scripts_dir / "signing_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.signing_config.update(config)
                print(f"✅ Signing configuration loaded from {config_file}")
                return True
            except Exception as e:
                print(f"⚠️ Could not load signing config: {e}")

        return False

    def create_signing_config_template(self):
        """Create a template signing configuration file"""
        config_file = self.scripts_dir / "signing_config.json"

        template_config = {
            "certificate_path": "path/to/your/certificate.p12",
            "certificate_password": "your_certificate_password",
            "timestamp_url": "http://timestamp.digicert.com",
            "description": "Phần mềm Quản lý Cám - Trại Gà",
            "url": "https://github.com/Minh-Tan_Phat",
            "instructions": [
                "1. Replace certificate_path with your actual certificate file path",
                "2. Replace certificate_password with your certificate password",
                "3. Optionally change timestamp_url to your preferred timestamp server",
                "4. Remove this instructions section when configured"
            ]
        }

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=4, ensure_ascii=False)
            print(f"✅ Signing configuration template created: {config_file}")
            print("📝 Please edit the configuration file with your certificate details")
            return True
        except Exception as e:
            print(f"❌ Could not create signing config template: {e}")
            return False

    def sign_file(self, file_path):
        """Sign a single file with digital certificate"""
        if not hasattr(self, 'signtool_path'):
            print("❌ SignTool not available")
            return False

        if not self.signing_config["certificate_path"]:
            print("❌ Certificate path not configured")
            return False

        cert_path = Path(self.signing_config["certificate_path"])
        if not cert_path.exists():
            print(f"❌ Certificate file not found: {cert_path}")
            return False

        # Build signtool command
        cmd = [
            self.signtool_path,
            "sign",
            "/f", str(cert_path),
            "/p", self.signing_config["certificate_password"],
            "/t", self.signing_config["timestamp_url"],
            "/d", self.signing_config["description"],
            "/du", self.signing_config["url"],
            "/v",
            str(file_path)
        ]

        try:
            print(f"🔐 Signing {file_path.name}...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Successfully signed: {file_path.name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Signing failed for {file_path.name}: {e}")
            print(f"STDERR: {e.stderr}")
            return False

    def sign_all_installers(self):
        """Sign all installer files in the output directory"""
        if not self.load_signing_config():
            print("⚠️ No signing configuration found. Creating template...")
            self.create_signing_config_template()
            return False

        tools_status = self.check_signing_tools()
        if not tools_status["signtool"]:
            print("❌ Code signing tools not available")
            return False

        # Find installer files to sign
        installer_files = []
        for pattern in ["*.exe", "*.msi"]:
            installer_files.extend(self.output_dir.glob(pattern))

        if not installer_files:
            print("⚠️ No installer files found to sign")
            return False

        success_count = 0
        for file_path in installer_files:
            if self.sign_file(file_path):
                success_count += 1

        print(f"\n📊 Signing Summary:")
        print(f"   Total files: {len(installer_files)}")
        print(f"   Successfully signed: {success_count}")
        print(f"   Failed: {len(installer_files) - success_count}")

        return success_count == len(installer_files)

    def verify_signatures(self):
        """Verify digital signatures of signed files"""
        if not hasattr(self, 'signtool_path'):
            print("❌ SignTool not available for verification")
            return False

        # Find signed files
        signed_files = []
        for pattern in ["*.exe", "*.msi"]:
            signed_files.extend(self.output_dir.glob(pattern))

        if not signed_files:
            print("⚠️ No files found to verify")
            return False

        print("🔍 Verifying digital signatures...")

        all_verified = True
        for file_path in signed_files:
            cmd = [self.signtool_path, "verify", "/pa", "/v", str(file_path)]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✅ {file_path.name}: Signature valid")
            except subprocess.CalledProcessError as e:
                print(f"❌ {file_path.name}: Signature verification failed")
                all_verified = False

        return all_verified

def main():
    """Main entry point"""
    print("🔐 Code Signing Manager for Windows Installers")
    print("=" * 60)

    manager = CodeSigningManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "sign":
            success = manager.sign_all_installers()
            return 0 if success else 1
        elif command == "verify":
            success = manager.verify_signatures()
            return 0 if success else 1
        elif command == "config":
            success = manager.create_signing_config_template()
            return 0 if success else 1
        else:
            print(f"Unknown command: {command}")
            print("Usage: python sign_installer.py [sign|verify|config]")
            return 1
    else:
        # Interactive mode
        print("Available commands:")
        print("1. Sign all installers")
        print("2. Verify signatures")
        print("3. Create configuration template")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ")

        if choice == "1":
            manager.sign_all_installers()
        elif choice == "2":
            manager.verify_signatures()
        elif choice == "3":
            manager.create_signing_config_template()
        elif choice == "4":
            print("Goodbye!")
        else:
            print("Invalid choice")

        return 0

if __name__ == "__main__":
    sys.exit(main())
