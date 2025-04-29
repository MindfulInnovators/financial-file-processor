#!/usr/bin/env python3
import zipfile
import os
from pathlib import Path

def create_zip_archive(zip_filename, source_dir):
    """Creates a zip archive of the specified source directory."""
    source_path = Path(source_dir)
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_path.rglob('*'):
            # Exclude __pycache__ and .git directories/files
            if "__pycache__" in file_path.parts or ".git" in file_path.parts:
                continue
            # Explicitly exclude the 'pages' directory
            if file_path.is_dir() and file_path.name == 'pages':
                 print(f"Skipping directory: {file_path}")
                 continue # Don't add the directory itself
            # Check if the file is within the 'pages' directory
            if 'pages' in file_path.relative_to(source_path).parts:
                 print(f"Skipping file within pages dir: {file_path}")
                 continue # Skip files within the pages directory
                 
            # Add file to zip
            zipf.write(file_path, file_path.relative_to(source_path))
            # print(f"Adding {file_path.relative_to(source_path)}") # Reduce verbosity

if __name__ == "__main__":
    zip_filename = "/home/ubuntu/financial_app_final_v10_syntax_fixed.zip"
    source_directory = "/home/ubuntu/financial_app"
    
    print(f"Creating zip archive: {zip_filename} from {source_directory}")
    create_zip_archive(zip_filename, source_directory)
    print(f"Successfully created {zip_filename}")
