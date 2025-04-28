# Financial File Processor - Documentation

## Overview
This application is a Python-based web app that allows users to upload financial files (Excel, CSV, PDF, or Images) and processes them to extract and categorize financial transactions. The app uses various Python libraries for parsing different file types and integrates with OpenAI's GPT-4 API to categorize transactions into standard accounting categories following New Zealand English spelling conventions.

## Features
- Upload and process multiple file types (Excel, CSV, PDF, Images)
- Extract structured financial data (description, amount, date)
- AI-powered transaction categorization using OpenAI's API
- Interactive data visualization with charts and tables
- Download categorized data as Excel files
- Track upload history

## Installation

### Prerequisites
- Python 3.10 or higher
- OpenAI API key

### Setup
1. Clone the repository or download the source code
2. Install the required dependencies:
   ```
   pip install pandas openpyxl pdfplumber pytesseract streamlit fastapi uvicorn python-multipart python-dotenv matplotlib seaborn openai Pillow
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Running the Application
1. Navigate to the application directory
2. Run the application using the provided script:
   ```
   ./run_app.sh
   ```
   Or directly with Streamlit:
   ```
   streamlit run app.py
   ```
3. Access the application in your web browser at the URL provided in the terminal (typically http://localhost:8501)

### Using the Application
1. **Upload Files**: Use the file uploader in the sidebar to select and upload a financial file (Excel, CSV, PDF, or Image)
2. **View Extracted Data**: After uploading, the application will extract structured data from the file and display it in the "Extracted Data" tab
3. **View Categorized Data**: The application will automatically categorize the transactions using AI and display the results in the "Categorized Data" tab
4. **Visualize Data**: The "Categorized Data" tab includes various charts and visualizations of the financial data
5. **Download Results**: Use the download button to save the categorized data as an Excel file
6. **View Upload History**: The sidebar displays a history of all uploaded files

## File Structure
```
financial_app/
├── app.py                  # Main application file
├── .env                    # Environment variables (API keys)
├── .env.example            # Example environment file
├── run_app.sh              # Script to run the application
├── create_sample_data.py   # Script to generate sample data
├── visualization.py        # Data visualization components
├── download.py             # Download functionality
├── history.py              # Upload history management
├── parsers/
│   ├── excel_parser.py     # Excel file parser
│   ├── csv_parser.py       # CSV file parser
│   ├── pdf_parser.py       # PDF file parser
│   ├── image_parser.py     # Image file parser
│   └── openai_integration.py # OpenAI API integration
├── uploads/                # Directory for uploaded files
├── data/                   # Directory for processed data
│   ├── sample_financial_data.csv  # Sample data for testing
│   ├── sample_financial_data.xlsx # Sample data for testing
│   └── upload_history.json        # Upload history storage
└── static/                 # Static files (if any)
```

## Technical Details

### Parsers
- **Excel Parser**: Uses pandas and openpyxl to extract data from Excel files
- **CSV Parser**: Uses pandas to extract data from CSV files
- **PDF Parser**: Uses pdfplumber to extract text and tables from PDF files
- **Image Parser**: Uses pytesseract (OCR) to extract text from images

### OpenAI Integration
- Uses OpenAI's API to categorize transactions into standard accounting categories
- Follows New Zealand English spelling conventions
- Handles API errors gracefully with fallback to "Uncategorized"

### Data Visualization
- Uses matplotlib and streamlit for interactive charts and tables
- Provides multiple visualization types (bar charts, pie charts)
- Color-coded categories for better visual understanding

### Data Storage
- Stores uploaded files in the uploads directory
- Tracks upload history in a JSON file
- Allows downloading processed data as Excel files

## Troubleshooting
- **API Key Issues**: Ensure your OpenAI API key is correctly set in the .env file
- **File Parsing Errors**: Check that your files are in the correct format and contain the expected data
- **OCR Quality**: For image files, ensure good image quality for better OCR results

## Extending the Application
- Add support for more file types
- Implement custom categorization rules
- Add more visualization options
- Implement user authentication
- Add database integration for persistent storage
