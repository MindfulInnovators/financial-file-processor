# Financial File Processor

A Python-based web application for processing financial files with AI-powered categorization and visualization.

## Features

- **File Upload**: Support for Excel, CSV, PDF, and image files
- **Intelligent Parsing**: Extract structured data from various financial document formats
- **Two-Level Categorization**: AI-powered categorization with main categories and subcategories
- **Interactive Dashboard**: Modern visualization with filtering capabilities
- **Download**: Export categorized data as Excel files
- **Upload History**: Track previous file uploads

## Modern Dashboard Features

- Interactive charts using Plotly
- Date range filtering
- Category and subcategory filtering
- Treemap visualization for expense breakdown
- Pie chart for revenue sources
- Key financial metrics display
- Responsive design

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Local Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the initialization script:
   ```
   ./init.sh
   ```

## Usage

1. Start the application:
   ```
   ./run_app.sh
   ```
   Or manually:
   ```
   streamlit run app.py
   ```
2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)
3. Upload a financial file using the sidebar uploader
4. Select whether to use the GPT-powered intelligent parser
5. View extracted data in the "Extracted Data" tab
6. Explore the interactive dashboard in the "Categorized Data" tab
7. Download the categorized data using the download button

## Deployment to Streamlit Cloud

1. Create a GitHub repository with your application code
2. Sign up for Streamlit Community Cloud (it's free)
3. Connect your GitHub repository to Streamlit Community Cloud
4. Set the main file path to "app.py"
5. Add your OpenAI API key to the Streamlit Cloud secrets in this format:
   ```
   OPENAI_API_KEY = "your_api_key_here"
   ```

## GPT-Powered Intelligent Parser

The application includes a powerful GPT-based parser that can:

- Automatically detect document type (transaction list, profit and loss, balance sheet)
- Extract structured data from complex financial documents
- Organize data with two-level categorization (main_category and subcategory)
- Handle various formats and layouts

## File Structure

- `app.py`: Main Streamlit application
- `parsers/`: File parsing modules
  - `excel_parser.py`: Excel file parser
  - `csv_parser.py`: CSV file parser
  - `pdf_parser.py`: PDF file parser
  - `image_parser.py`: Image file parser (OCR)
  - `openai_integration.py`: OpenAI API integration
  - `gpt_parser.py`: GPT-powered intelligent parser
- `visualization.py`: Data visualization components
- `download.py`: Download functionality
- `history.py`: Upload history management
- `data/`: Directory for sample data and history
- `uploads/`: Directory for uploaded files

## License

This project is licensed under the MIT License - see the LICENSE file for details.
