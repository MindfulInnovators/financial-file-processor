# Financial File Processor

A Python-based web application that allows users to upload financial files (Excel, CSV, PDF, or Images), extracts structured data, and categorizes transactions using AI.

## Features

- Upload and process multiple file types (Excel, CSV, PDF, Images)
- Extract structured financial data (description, amount, date)
- AI-powered transaction categorization using OpenAI's API
- Interactive data visualization with charts and tables
- Download categorized data as Excel files
- Track upload history

## Demo

Visit the live application at [Streamlit Community Cloud](https://financial-file-processor.streamlit.app)

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
│   └── openai_integration.py # OpenAI API integration
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
