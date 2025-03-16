#!/bin/bash
# Archive Code Utility
# Archives code files with version numbers for tracking iterations
#
# Usage: 
#   ./archive_code.sh [version]                    - Archive all Python files in src
#   ./archive_code.sh [version] [file_path]        - Archive a specific file
#   ./archive_code.sh [version] [file1] [file2]... - Archive multiple specific files

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Check if version argument was provided
if [ $# -lt 1 ]; then
    echo "Error: Version number required."
    echo "Usage:"
    echo "  ./archive_code.sh [version]                    - Archive all Python files in src"
    echo "  ./archive_code.sh [version] [file_path]        - Archive a specific file"
    echo "  ./archive_code.sh [version] [file1] [file2]... - Archive multiple specific files"
    echo "Example: ./archive_code.sh v0.1"
    echo "Example: ./archive_code.sh v0.1 src/schema.py src/app.py"
    exit 1
fi

VERSION="$1"
# Check if version starts with 'v', if not prepend it
if [[ ! $VERSION =~ ^v ]]; then
    VERSION="v$VERSION"
fi

# Function to archive a file
archive_file() {
    local file="$1"
    
    # Skip if file doesn't exist
    if [ ! -f "$PROJECT_ROOT/$file" ]; then
        echo "Warning: File $file does not exist. Skipping."
        return
    fi
    
    local relative_path="${file#$PROJECT_ROOT/}"
    local dir=$(dirname "$relative_path")
    local filename=$(basename "$file")
    local base="${filename%.*}"
    local ext="${filename##*.}"
    
    # Skip if the file is __init__.py
    if [ "$filename" = "__init__.py" ]; then
        echo "Skipping __init__.py file: $relative_path"
        return
    fi
    
    # Skip if the file already has a version pattern (like file-v0.1.py)
    if [[ $base =~ -v[0-9]+(\.[0-9]+)* ]]; then
        echo "Skipping already versioned file: $relative_path"
        return
    fi
    
    local archive_path="$PROJECT_ROOT/$dir/$base-$VERSION.$ext"
    
    cp "$PROJECT_ROOT/$file" "$archive_path"
    echo "Archived $relative_path to $dir/$base-$VERSION.$ext"
}

# If additional arguments are provided, archive those specific files
if [ $# -gt 1 ]; then
    echo "Archiving specified files with version $VERSION..."
    
    # Loop through all arguments except the first one (version)
    for ((i=2; i<=$#; i++)); do
        file="${!i}"
        archive_file "$file"
    done
    
    echo "Archiving complete!"
    exit 0
fi

# Otherwise, archive all Python files in src directory
echo "Archiving all Python files in src directory with version $VERSION..."

# Find all .py files in src directory and archive them
# Exclude files that already have a version pattern
find "$PROJECT_ROOT/src" -name "*.py" -type f | while read -r file; do
    # Get the relative path from PROJECT_ROOT
    relative_path="${file#$PROJECT_ROOT/}"
    archive_file "$relative_path"
done

echo "Archiving complete!"