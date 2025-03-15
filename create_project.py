#!/usr/bin/env python3
"""
Project Setup Script for st_agent_hub

This script creates only the directory structure for the st_agent_hub project.
You can then manually add files to each directory.

Usage:
    python create_project.py [project_path]
    
    If project_path is not provided, it will create the project in the current directory.
"""

import os
import sys
from pathlib import Path

def main():
    """Main function to create the project structure."""
    # Determine the project root directory
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "st_agent_hub"
    
    project_path = Path(project_root)
    
    print(f"Creating project structure in: {project_path.absolute()}")
    
    # Directories to create
    directories = [
        "src",
        "docs",
        "docs/images",
        "docs/design",
        "dev",
        "dev/notebooks",
        "tests",
        "scripts",
        "data"  # For JSON database files
    ]
    
    # Create directory structure
    for directory in directories:
        dir_path = project_path / directory
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create empty placeholder files
    placeholder_files = [
        "README.md",
        "requirements.txt",
        ".gitignore",
        "LICENSE.md",
        "src/schema.py",
        "src/database.py",
        "src/app.py",
        "src/main.py",
        "src/__init__.py",
        "tests/__init__.py",
        "tests/test_schema.py",
        "docs/design/agent_schema_design.md",
        "scripts/run_app.sh"
    ]
    
    for filename in placeholder_files:
        file_path = project_path / filename
        with open(file_path, 'w') as f:
            f.write(f"# Placeholder file: {filename}\n# Replace with actual content\n")
        print(f"Created placeholder file: {file_path}")
    
    # Make the run script executable
    run_script_path = project_path / "scripts" / "run_app.sh"
    os.chmod(run_script_path, 0o755)  # Make executable
    
    # Done!
    print("\nProject structure setup complete!")
    print(f"Project created at: {project_path.absolute()}")
    print("\nNext steps:")
    print("1. Add content to the placeholder files")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run: streamlit run src/main.py")

# Run the script
if __name__ == "__main__":
    main()