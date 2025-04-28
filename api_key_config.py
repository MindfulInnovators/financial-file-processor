import streamlit as st
import os
from dotenv import load_dotenv

def save_api_key():
    """
    Streamlit app to save OpenAI API key to .env file
    """
    st.title("OpenAI API Key Configuration")
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    
    # Get current API key if it exists
    current_key = os.getenv("OPENAI_API_KEY", "")
    
    # Create input field for API key
    api_key = st.text_input(
        "Enter your OpenAI API Key",
        value=current_key,
        type="password",
        help="Your API key will be saved to the .env file in the application directory."
    )
    
    # Save button
    if st.button("Save API Key"):
        try:
            # Read existing .env file if it exists
            env_content = ""
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    env_content = f.read()
            
            # Check if OPENAI_API_KEY already exists in the file
            if "OPENAI_API_KEY=" in env_content:
                # Replace existing key
                env_content = env_content.replace(
                    f"OPENAI_API_KEY={current_key}",
                    f"OPENAI_API_KEY={api_key}"
                )
            else:
                # Add new key
                env_content += f"\nOPENAI_API_KEY={api_key}\n"
            
            # Write updated content to .env file
            with open(env_file, "w") as f:
                f.write(env_content)
            
            st.success("API Key saved successfully! Please restart the application for changes to take effect.")
            
        except Exception as e:
            st.error(f"Error saving API key: {e}")
    
    st.divider()
    
    # Instructions
    st.subheader("Instructions")
    st.markdown("""
    1. Get your OpenAI API key from [OpenAI's website](https://platform.openai.com/api-keys)
    2. Enter your API key in the field above
    3. Click the "Save API Key" button
    4. Restart the application for the changes to take effect
    
    Your API key will be stored locally in the .env file and will not be shared with anyone.
    """)
    
    # Return to main app button
    if st.button("Return to Main Application"):
        st.switch_page("app.py")

if __name__ == "__main__":
    save_api_key()
