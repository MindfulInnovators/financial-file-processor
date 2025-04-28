import os
import shutil
import zipfile
from datetime import datetime

# Define directories
project_dir = "/home/ubuntu/financial_app"
output_dir = "/home/ubuntu"
output_filename = "financial_app_revised_parser.zip"

# Create a temporary directory for the revised version
temp_dir = os.path.join(output_dir, "financial_app_revised")
os.makedirs(temp_dir, exist_ok=True)

# Copy all files from the project directory to the temporary directory
for item in os.listdir(project_dir):
    source = os.path.join(project_dir, item)
    destination = os.path.join(temp_dir, item)
    
    if os.path.isdir(source):
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)

# Create a README file specifically for the revised version
readme_content = f"""# Financial File Processor with Improved GPT Parser

A Python-based web application that allows users to upload financial files (Excel, CSV, PDF, or Images), extracts structured data, and categorizes transactions using AI.

## New Improved GPT Parser

The application now features a completely revised GPT-powered parser that:

- **Transforms Unformatted Documents into Structured Tables**: Instead of just extracting specific fields, the parser now transforms entire financial documents into standardized tables.
- **Handles Complex Financial Documents**: Works with profit and loss statements, balance sheets, transaction lists, and other financial document types.
- **Creates Consistent Data Structure**: Extracts date, category, subcategory, description, and amount for all financial items.
- **Preserves All Financial Data**: Captures all relevant financial information from the document, not just predefined fields.

## How the New Parser Works

1. The parser extracts raw content from the uploaded file (Excel, CSV, PDF, or image)
2. It sends the content to GPT with a specialized prompt that instructs it to:
   - Analyze the document to determine its type
   - Extract all financial data
   - Transform the data into a standardized table format with consistent columns
   - Return the data as a structured JSON object
3. The application then converts this JSON into a pandas DataFrame for processing
4. The standardized data is displayed and can be categorized, visualized, and downloaded

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
│   └── gpt_parser.py       # REVISED: GPT-powered table transformation parser
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

# Write the revised README
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

# Create a zip file of the revised project
output_path = os.path.join(output_dir, output_filename)
with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zipf.write(file_path, arcname)

print(f"Revised project packaged successfully: {output_path}")
