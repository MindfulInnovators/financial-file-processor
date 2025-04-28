import os
import shutil
import zipfile

def create_zip_archive():
    """
    Create a zip archive of the financial app project.
    """
    # Define the source directory and zip file path
    source_dir = '/home/ubuntu/financial_app'
    zip_file = '/home/ubuntu/financial_app_project.zip'
    
    # Create a zip file
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for root, dirs, files in os.walk(source_dir):
            # Skip __pycache__ directories and streamlit.log
            if '__pycache__' in root or '.streamlit' in root:
                continue
                
            for file in files:
                # Skip log files and __pycache__ files
                if file == 'streamlit.log' or file.endswith('.pyc'):
                    continue
                    
                # Get the full file path
                file_path = os.path.join(root, file)
                
                # Calculate the relative path for the archive
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                
                # Add the file to the zip archive
                zipf.write(file_path, rel_path)
    
    return zip_file

if __name__ == "__main__":
    zip_file = create_zip_archive()
    print(f"Created zip archive: {zip_file}")
