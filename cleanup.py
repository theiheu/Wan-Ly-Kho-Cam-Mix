import os
import glob
import shutil

# Create tools directory if it doesn't exist
if not os.path.exists("tools"):
    os.makedirs("tools")

# Move useful scripts to tools directory
useful_scripts = ["direct_fix.py"]
for script in useful_scripts:
    if os.path.exists(script):
        shutil.copy(script, os.path.join("tools", script))
        print(f"Copied {script} to tools directory")

# List of temporary files to delete
temp_files = [
    "*.py",  # All Python scripts in the root directory except run.py
    "*.txt"  # All text files in the root directory except README.md
]

# Files to keep
keep_files = [
    "run.py",
    "requirements.txt",
    "README.md",
    ".gitignore"
]

# Process each file pattern
for pattern in temp_files:
    for file_path in glob.glob(pattern):
        # Skip files we want to keep
        if os.path.basename(file_path) in keep_files:
            continue

        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Skip files in tools directory
        if file_path.startswith("tools/"):
            continue

        # Delete the file
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

print("\nCleanup completed!")
print("Temporary files have been removed. The application is now optimized and organized.")