import os
import shutil
import zipfile
from datetime import datetime

# Define directories
project_dir = "/home/ubuntu/financial_app"
output_dir = "/home/ubuntu"
output_filename = "financial_app_final_v3.zip"

# Create a temporary directory for the final version
temp_dir = os.path.join(output_dir, "financial_app_final_v3")
os.makedirs(temp_dir, exist_ok=True)

# Copy all files from the project directory to the temporary directory
for item in os.listdir(project_dir):
    source = os.path.join(project_dir, item)
    destination = os.path.join(temp_dir, item)
    
    # Skip the pages directory if it somehow still exists
    if item == "pages":
        continue
        
    if os.path.isdir(source):
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)

# Create a README file specifically for the final version
readme_content = f"""# Financial File Processor - Final Version 3

A Python-based web application that allows users to upload financial files (Excel, CSV, PDF, or Images), extracts structured data, and categorizes transactions using AI.

## Final Fixes (v3)

- **Fixed UnboundLocalError**: Resolved an error related to `st.set_page_config` caused by a duplicate Streamlit import.
- **Completely Removed API Key Configuration Page**: The separate page for API key configuration has been removed, along with all references to it in the main application.
- **Updated API Key Detection**: The application now properly checks for API keys in both environment variables and Streamlit secrets.
- **Aligned GPT Parser Categories**: The GPT parser uses the specific accounting categories requested, ensuring consistency in data transformation.

## Key Features

- **GPT-Powered Intelligent Parser**: Transforms unformatted financial documents (profit and loss, balance sheets, transaction lists) into structured tables using specific accounting categories.
- **Handles Complex Financial Documents**: Works with various layouts and formats.
- **Consistent Data Structure**: Extracts date, category (aligned with accounting standards), description, and amount.
- **Upload and process multiple file types** (Excel, CSV, PDF, Images)
- **AI-powered transaction categorization** using OpenAI's API
- **Interactive data visualization** with charts and tables
- **Download categorized data** as Excel files
- **Track upload history**

## Requirements

- Python 3.10 or higher
- OpenAI API key (configured in Streamlit Cloud secrets)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/financial-file-processor.git
cd financial-file-processor

# Install dependencies
pip install -r requirements.txt

# Configure OpenAI API key in Streamlit Cloud secrets
# Go to App Settings -> Secrets and add:
# OPENAI_API_KEY = "your_api_key_here"
```

## Usage

```bash
# Run the application locally (optional)
streamlit run app.py
```

Then open your browser and navigate to http://localhost:8501

## Deployment

This application is designed for deployment to Streamlit Community Cloud:

1. Fork this repository to your GitHub account
2. Sign up for [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your forked repository
4. Add your OpenAI API key to the Streamlit Cloud secrets (as shown in Installation)
5. Deploy the app

## File Structure

```
financial_app/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore file
├── README.md               # This file
├── create_sample_data.py   # Script to generate sample data
├── visualization.py        # Data visualization components
├── download.py             # Download functionality
├── history.py              # Upload history management
├── parsers/
│   ├── excel_parser.py     # Excel file parser
│   ├── csv_parser.py       # CSV file parser
│   ├── pdf_parser.py       # PDF file parser
│   ├── image_parser.py     # Image file parser
│   ├── openai_integration.py # OpenAI API integration
│   └── gpt_parser.py       # REVISED: GPT-powered table transformation parser (with aligned categories)
├── uploads/                # Directory for uploaded files
└── data/                   # Directory for processed data
    ├── sample_financial_data.csv  # Sample data for testing
    ├── sample_financial_data.xlsx # Sample data for testing
    └── upload_history.json        # Upload history storage
```

## License

MIT

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

Last updated: {datetime.now().strftime("%Y-%m-%d")}
"""

# Write the final README
with open(os.path.join(temp_dir, "README.md"), "w") as f:
    f.write(readme_content)

# Update requirements.txt to include all necessary packages
requirements_content = """pandas
openpyxl
pdfplumber
pytesseract
streamlit
python-dotenv
matplotlib
seaborn
openai
Pillow
numpy
"""

with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
    f.write(requirements_content)

# Create a zip file of the final project
output_path = os.path.join(output_dir, output_filename)
with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        # Exclude the temporary directory itself from the archive path
        arc_root = os.path.relpath(root, temp_dir)
        # Skip the root directory entry itself
        if arc_root == '.':
            arc_root = ''
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.join(arc_root, file)
            zipf.write(file_path, arcname)

# Clean up temporary directory
shutil.rmtree(temp_dir)

print(f"Final fixed project (v3) packaged successfully: {output_path}")
