import os
import shutil
import zipfile
from datetime import datetime

# Define directories
project_dir = "/home/ubuntu/financial_app"
output_dir = "/home/ubuntu"
output_filename = "financial_app_enhanced.zip"

# Create a temporary directory for the enhanced version
temp_dir = os.path.join(output_dir, "financial_app_enhanced")
os.makedirs(temp_dir, exist_ok=True)

# Copy all files from the project directory to the temporary directory
for item in os.listdir(project_dir):
    source = os.path.join(project_dir, item)
    destination = os.path.join(temp_dir, item)
    
    if os.path.isdir(source):
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)

# Create a README file specifically for the enhanced version
readme_content = f"""# Enhanced Financial File Processor

A Python-based web application that allows users to upload financial files (Excel, CSV, PDF, or Images), extracts structured data, and categorizes transactions using AI.

## New Features in Enhanced Version

- **GPT-Powered Intelligent Parser**: Automatically detects and processes different financial document types:
  - Transaction Lists
  - Profit and Loss Statements
  - Balance Sheets
  - Other financial documents

- **Document Type Detection**: Automatically identifies the type of financial document being uploaded
- **Specialized Extraction**: Uses different extraction strategies based on document type
- **Flexible Format Handling**: Works with complex financial report layouts

## Original Features

- Upload and process multiple file types (Excel, CSV, PDF, Images)
- Extract structured financial data (description, amount, date)
- AI-powered transaction categorization using OpenAI's API
- Interactive data visualization with charts and tables
- Download categorized data as Excel files
- Track upload history

## Requirements

- Python 3.10 or higher
- OpenAI API key

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/financial-file-processor.git
cd financial-file-processor

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key
# Option 1: Create a .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Option 2: Use the API Key Configuration page in the app
```

## Usage

```bash
# Run the application
streamlit run app.py
```

Then open your browser and navigate to http://localhost:8501

## How to Use the GPT-Powered Parser

1. Upload any financial document (Excel, CSV, PDF, or Image)
2. Ensure the "Use GPT-powered intelligent parser" checkbox is selected in the sidebar
3. The application will:
   - Detect the document type (transaction list, profit and loss, balance sheet)
   - Extract structured data using specialized prompts for each document type
   - Display the extracted data in a standardized format
   - Categorize the transactions using AI

## Deployment

This application can be deployed to Streamlit Community Cloud:

1. Fork this repository to your GitHub account
2. Sign up for [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your forked repository
4. Add your OpenAI API key to the Streamlit Cloud secrets
5. Deploy the app

## File Structure

```
financial_app/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore file
├── README.md               # This file
├── create_sample_data.py   # Script to generate sample data
├── create_secrets.py       # Script to create secrets.toml
├── visualization.py        # Data visualization components
├── download.py             # Download functionality
├── history.py              # Upload history management
├── pages/
│   └── api_key_config.py   # API key configuration page
├── parsers/
│   ├── excel_parser.py     # Excel file parser
│   ├── csv_parser.py       # CSV file parser
│   ├── pdf_parser.py       # PDF file parser
│   ├── image_parser.py     # Image file parser
│   ├── openai_integration.py # OpenAI API integration
│   └── gpt_parser.py       # NEW: GPT-powered intelligent parser
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

# Write the enhanced README
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

# Create a zip file of the enhanced project
output_path = os.path.join(output_dir, output_filename)
with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zipf.write(file_path, arcname)

print(f"Enhanced project packaged successfully: {output_path}")
