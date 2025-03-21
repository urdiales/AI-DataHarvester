import os
import streamlit as st
import json
import base64
import requests
from datetime import datetime
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse import parse_with_ollama, AVAILABLE_MODELS
from logger_config import setup_logger
from health import add_health_status_sidebar

# Set up logger for this module
logger = setup_logger(__name__, os.path.join("logs", "streamlit.log"))

# Initialize the app
logger.info("Starting AI DataHarvester application")

# Initialize session state for health override if not already done
if "ollama_override" not in st.session_state:
    st.session_state.ollama_override = False


def safe_scrape_website(url):
    """Safely scrape a website and handle exceptions appropriately in Streamlit."""
    try:
        st.info("Scraping the website... This may take a few moments.")
        logger.info(f"Starting to scrape website: {url}")

        dom_content = scrape_website(url)

        try:
            body_content = extract_body_content(dom_content)
        except Exception as e:
            st.error(f"Failed to extract body content: {str(e)}")
            logger.error(f"Body extraction error for {url}: {str(e)}")
            return None

        try:
            cleaned_content = clean_body_content(body_content)
        except Exception as e:
            st.error(f"Failed to clean content: {str(e)}")
            logger.error(f"Content cleaning error for {url}: {str(e)}")
            return None

        return cleaned_content

    except ValueError as e:
        st.error(f"Invalid URL format: {str(e)}")
        logger.error(f"URL validation error: {str(e)}")
    except ConnectionError as e:
        st.error(f"Failed to connect to the website: {str(e)}")
        logger.error(f"Connection error for {url}: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred during scraping: {str(e)}")
        logger.error(f"Unexpected scraping error for {url}: {str(e)}", exc_info=True)

    return None


def get_download_link(content, filename, text):
    """Generate a download link for the given content."""
    if isinstance(content, dict):
        content_str = json.dumps(content, indent=2)
    else:
        content_str = str(content)

    b64 = base64.b64encode(content_str.encode()).decode()
    href = f"data:file/txt;base64,{b64}"
    return f'<a href="{href}" download="{filename}">{text}</a>'


def reset_session():
    """Reset all session state variables related to scraping and parsing."""
    if "dom_content" in st.session_state:
        del st.session_state.dom_content
    if "parsed_result" in st.session_state:
        del st.session_state.parsed_result
    if "url" in st.session_state:
        del st.session_state.url
    logger.info("Session state reset")


def send_to_webhook(data, webhook_url):
    """
    Send data to a webhook URL.

    Args:
        data: Dictionary of data to send
        webhook_url: URL to send the data to

    Returns:
        bool: Success status
        str: Message
    """
    try:
        # Add timestamp if not present
        if "timestamp" not in data or not data["timestamp"]:
            data["timestamp"] = datetime.now().isoformat()

        # Make the POST request
        response = requests.post(
            webhook_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        # Check if request was successful
        if response.status_code >= 200 and response.status_code < 300:
            logger.info(f"Successfully sent data to webhook: {webhook_url}")
            return True, f"Data sent successfully (Status: {response.status_code})"
        else:
            logger.error(
                f"Failed to send data to webhook. Status code: {response.status_code}"
            )
            return False, f"Error: Server returned status code {response.status_code}"

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending data to webhook: {str(e)}")
        return False, f"Error: {str(e)}"


# Add health status sidebar - MUST be before any other Streamlit UI elements
add_health_status_sidebar()

# Streamlit UI
st.title("AI DataHarvester")
logger.info("UI initialized")

# URL input field
if "url" in st.session_state:
    url = st.text_input("Enter Website URL", value=st.session_state.url)
else:
    url = st.text_input("Enter Website URL")

# Control buttons in their own row
control_col1, control_col2 = st.columns(2)

with control_col1:
    # Reset button
    if st.button("🔄 Reset All Data", use_container_width=True):
        reset_session()
        st.success("All data has been reset")

# Step 1: Scrape the Website
if st.button("Scrape Website"):
    logger.info(f"Scrape button clicked for URL: {url}")
    if url:
        # Save URL to session state
        st.session_state.url = url

        with st.spinner("Scraping website..."):
            cleaned_content = safe_scrape_website(url)

            if cleaned_content:
                st.success("Website scraped successfully!")
                logger.info("Website scraped successfully")

                # Store the DOM content in Streamlit session state
                st.session_state.dom_content = cleaned_content

                # Display the DOM content in an expandable text box
                with st.expander("View DOM Content"):
                    st.text_area("DOM Content", cleaned_content, height=300)
    else:
        st.error("Please enter a URL first")
        logger.warning("Scrape button clicked without URL")

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    # Add model selection dropdown
    model_name = st.selectbox(
        "Select LLM Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=1,  # Default to llama3.2
    )

    if st.button("Parse Content"):
        logger.info(f"Parse button clicked with model: {model_name}")
        if parse_description:
            with st.spinner("Parsing the content..."):
                logger.info(f"Parsing content with description: {parse_description}")

                try:
                    # Parse the content with Ollama
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    parsed_result = parse_with_ollama(
                        dom_chunks, parse_description, model_name
                    )

                    # Save parsed result to session state
                    st.session_state.parsed_result = parsed_result

                    # Display the parsed result
                    st.write(parsed_result)
                    logger.info("Content parsed successfully")
                except Exception as e:
                    st.error(f"Error parsing content: {str(e)}")
                    logger.error(f"Error during parsing: {str(e)}", exc_info=True)
        else:
            st.error("Please provide a description of what to parse")
            logger.warning("Parse button clicked without description")

# Step 3: Show download and webhook options if parsed result exists
if "parsed_result" in st.session_state:
    # Create JSON data structure
    json_data = {
        "url": st.session_state.get("url", ""),
        "parsed_content": st.session_state.parsed_result,
        "model_used": model_name if "model_name" in locals() else "unknown",
        "timestamp": datetime.now().isoformat(),
    }

    # Result action buttons (in a row with equal columns)
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        # Download button
        download_link = get_download_link(
            json_data, "parsed_content.json", "📥 Download Results as JSON"
        )
        st.markdown(download_link, unsafe_allow_html=True)

    with action_col2:
        # Webhook section
        # Input for webhook URL
        webhook_url = st.text_input(
            "Webhook URL",
            placeholder="https://your-webhook-endpoint.com",
            help="Enter the URL where you want to send the JSON data",
        )

        # Send to webhook button
        if st.button("📤 Send to Webhook", use_container_width=True):
            if webhook_url:
                with st.spinner("Sending data to webhook..."):
                    success, message = send_to_webhook(json_data, webhook_url)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.error("Please enter a webhook URL")

logger.info("Application UI fully rendered")
