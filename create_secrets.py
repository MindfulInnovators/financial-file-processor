import streamlit as st
import os
import json
from dotenv import load_dotenv

# Create a secrets.toml file for Streamlit Cloud deployment
def create_secrets_file():
    """
    Create a secrets.toml file for Streamlit Cloud deployment
    """
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    secrets_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
    secrets_file = os.path.join(secrets_dir, "secrets.toml")
    
    # Create .streamlit directory if it doesn't exist
    os.makedirs(secrets_dir, exist_ok=True)
    
    # Default content for secrets.toml
    secrets_content = """# .streamlit/secrets.toml

# OpenAI API key
OPENAI_API_KEY = ""  # Add your OpenAI API key here
"""
    
    # If .env file exists, read API key from it
    if os.path.exists(env_file):
        load_dotenv(env_file)
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            secrets_content = f"""# .streamlit/secrets.toml

# OpenAI API key
OPENAI_API_KEY = "{api_key}"
"""
    
    # Write secrets.toml file
    with open(secrets_file, "w") as f:
        f.write(secrets_content)
    
    print(f"Created secrets.toml file at {secrets_file}")
    return secrets_file

if __name__ == "__main__":
    create_secrets_file()
