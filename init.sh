#!/bin/bash

# Create a new .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit the .env file to add your OpenAI API key."
fi

# Generate sample data for testing
echo "Generating sample data for testing..."
python3 create_sample_data.py

# Start the application
echo "Starting the Financial File Processor application..."
echo "Press Ctrl+C to stop the application when finished."
streamlit run app.py
