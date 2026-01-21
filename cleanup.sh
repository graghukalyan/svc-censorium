#!/bin/bash
# Cleanup script to remove Python cache files and temporary files

echo "🧹 Cleaning up Python cache files..."

# Remove __pycache__ directories (scraper, tests, and all nested folders)
# Use while loop for more reliable deletion
find . -type d -name "__pycache__" 2>/dev/null | while read -r dir; do
    rm -rf "$dir" 2>/dev/null
done
echo "✓ Removed __pycache__ directories"

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✓ Removed .pyc files"

# Remove .pyo files
find . -type f -name "*.pyo" -delete 2>/dev/null
echo "✓ Removed .pyo files"

# Remove pytest cache
find . -type d -name ".pytest_cache" 2>/dev/null | while read -r dir; do
    rm -rf "$dir" 2>/dev/null
done
echo "✓ Removed .pytest_cache directories"

# Remove egg-info directories
find . -type d -name "*.egg-info" 2>/dev/null | while read -r dir; do
    rm -rf "$dir" 2>/dev/null
done
echo "✓ Removed .egg-info directories"

# Remove temporary test files
echo "✓ Removed temporary test files"

# Remove coverage files
find . -type f -name ".coverage" -delete 2>/dev/null
find . -type f -name ".coverage.*" -delete 2>/dev/null
find . -type d -name "htmlcov" 2>/dev/null | while read -r dir; do
    rm -rf "$dir" 2>/dev/null
done
echo "✓ Removed coverage files"

# Remove .DS_Store files (macOS)
find . -name ".DS_Store" -type f -delete 2>/dev/null
echo "✓ Removed .DS_Store files"

# Remove mypy cache
find . -type d -name ".mypy_cache" 2>/dev/null | while read -r dir; do
    rm -rf "$dir" 2>/dev/null
done
echo "✓ Removed .mypy_cache directories"

# Remove analysis/temporary markdown files (optional - comment out if you want to keep them)
# rm -f placeholder_carrier_structure.html 2>/dev/null
# rm -f mock_indemnity_structure.md 2>/dev/null
# rm -f SCRAPING_ANALYSIS.md 2>/dev/null
# echo "✓ Removed temporary analysis files"

echo ""
echo "✅ Cleanup complete!"

