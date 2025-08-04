#!/usr/bin/env python3
"""
Fix remaining ChickenFarmApp references
"""

import os
import re
from pathlib import Path

def find_and_fix_references():
    """Find and fix all ChickenFarmApp references"""

    project_root = Path(__file__).parent

    # Files to check
    files_to_check = [
        project_root / "src" / "main.py",
        project_root / "run.py",
    ]

    # Add all Python files in src
    src_dir = project_root / "src"
    if src_dir.exists():
        for py_file in src_dir.rglob("*.py"):
            files_to_check.append(py_file)

    replacements = [
        (r'ChickenFarmApp', 'Quan_Ly_Kho_Cam_Mix_App'),
        (r'chicken_farm_app', 'quan_ly_kho_cam_mix_app'),
        (r'ChickenFarm', 'Quan_Ly_Kho_Cam_Mix'),
        (r'chicken_farm', 'quan_ly_kho_cam_mix'),
    ]

    fixed_files = []

    for file_path in files_to_check:
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply replacements
            for old_pattern, new_pattern in replacements:
                content = re.sub(old_pattern, new_pattern, content)

            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path)
                print(f"✅ Fixed: {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    if fixed_files:
        print(f"\n🎉 Fixed {len(fixed_files)} files")
    else:
        print("\n✅ No references found to fix")

    return len(fixed_files) > 0

if __name__ == "__main__":
    find_and_fix_references()
