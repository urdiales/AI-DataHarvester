import requests
import os
import time
import streamlit as st
from logger_config import setup_logger

logger = setup_logger(__name__, os.path.join("logs", "health.log"))


def check_ollama_health(host=None, override=False):
    """
    Check if Ollama service is healthy by attempting to get model list.

    Args:
        host: Ollama API host (defaults to environment variable)
        override: If True, bypass actual health check and return healthy

    Returns:
        tuple: (is_healthy, message)
    """
    # If override is enabled, skip the actual health check
    if override:
        logger.info("Ollama health check bypassed due to manual override")
        return True, "Manually marked as healthy"

    if host is None:
        host = os.environ.get("OLLAMA_HOST", "http://ollama:11434")

    url = f"{host}/api/tags"

    try:
        # Increase timeout for slower networks/systems
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if not models:
                # Handle case where response is valid but no models are returned
                logger.warning(f"Ollama is running but no models are available")
                return True, "Healthy, but no models detected."

            available_models = [model["name"] for model in models]
            logger.info(f"Ollama is healthy. Available models: {available_models}")
            return True, f"Healthy. {len(available_models)} models available."
        else:
            logger.error(f"Ollama returned status code {response.status_code}")
            return False, f"Error: Status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Ollama service on any endpoint")
        return False, "Error: Connection failed"
    except requests.exceptions.Timeout:
        logger.error("Ollama service request timed out")
        return False, "Error: Connection timeout"
    except Exception as e:
        logger.error(f"Unexpected error checking Ollama health: {str(e)}")
        return False, f"Error: {str(e)}"


def check_brightdata_connectivity():
    """
    Check if Bright Data credentials are valid by testing connection.

    Returns:
        tuple: (is_healthy, message)
    """
    try:
        from selenium.webdriver.chromium.remote_connection import (
            ChromiumRemoteConnection,
        )
        import selenium.webdriver as webdriver

        BRIGHTDATA_USER = os.getenv("BRIGHTDATA_USER")
        BRIGHTDATA_PASSWORD = os.getenv("BRIGHTDATA_PASSWORD")

        if not BRIGHTDATA_USER or not BRIGHTDATA_PASSWORD:
            logger.error("Missing Bright Data credentials")
            return False, "Error: Missing credentials"

        AUTH = f"{BRIGHTDATA_USER}:{BRIGHTDATA_PASSWORD}"
        SBR_WEBDRIVER = f"https://{AUTH}@brd.superproxy.io:9515"

        try:
            # Test connection
            sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")
            options = webdriver.ChromeOptions()

            driver = webdriver.Remote(sbr_connection, options=options)
            driver.quit()

            logger.info("Bright Data connection successful")
            return True, "Healthy. Connection successful."
        except Exception as e:
            logger.error(f"Bright Data connection failed: {str(e)}")
            return False, f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error setting up Bright Data check: {str(e)}")
        return False, f"Setup error: {str(e)}"


def add_health_status_sidebar():
    """Add health status information to the Streamlit sidebar."""
    with st.sidebar:
        st.header("System Health")

        # Initialize the override flag if it doesn't exist
        if "ollama_override" not in st.session_state:
            st.session_state.ollama_override = False

        # Subheader for Ollama service
        st.subheader("Ollama LLM Service")

        # Check actual Ollama health status (for logging purposes)
        actual_status, actual_msg = check_ollama_health(override=False)

        # Display based on override status
        if st.session_state.ollama_override:
            # Show success message when overridden
            st.success("✓ Manually marked as healthy")

            # Add reset button
            if st.button("Reset Override (Check Actual Status)"):
                # Clear the override flag
                st.session_state.ollama_override = False
                # No rerun needed - will update on next render
        else:
            # Show actual status when not overridden
            if actual_status:
                st.success(actual_msg)
            else:
                # Show error and troubleshooting when there's a connection issue
                st.error(actual_msg)
                with st.expander("Troubleshooting"):
                    st.markdown(
                        """
                    If you're seeing a connection error but know Ollama is running:
                    
                    1. Check that the OLLAMA_HOST environment variable is set correctly
                    2. Ensure the Ollama container is running: `docker-compose ps`
                    3. Try restarting Ollama: `docker-compose restart ollama`
                    4. Check Ollama logs: `docker-compose logs ollama`
                    """
                    )

                    # Manual override option
                    if st.button("Override (Mark as Healthy)"):
                        st.session_state.ollama_override = True
                        # No rerun needed - will update on next render

        # Bright Data health check section
        st.subheader("Bright Data Service")
        if st.button("Check Bright Data Connection"):
            with st.spinner("Testing connection..."):
                bd_status, bd_msg = check_brightdata_connectivity()
                if bd_status:
                    st.success(bd_msg)
                else:
                    st.error(bd_msg)


def run_periodic_health_checks(interval_seconds=300):
    """
    Run periodic health checks and log results.
    This can be run in a background thread.

    Args:
        interval_seconds: Time between checks in seconds
    """
    while True:
        logger.info("Running periodic health checks")

        # Check Ollama - never use override for background checks
        ollama_status, ollama_msg = check_ollama_health(override=False)
        if not ollama_status:
            logger.warning(f"Ollama health check failed: {ollama_msg}")

        # Sleep until next check
        time.sleep(interval_seconds)


# Function to check overall application health for Docker healthcheck
def check_app_health():
    """
    Check if the application is healthy.
    Returns exit code 0 if healthy, 1 if unhealthy.
    """
    try:
        # Check Ollama - never use override for Docker health checks
        ollama_status, _ = check_ollama_health(override=False)
        if not ollama_status:
            return 1

        # Add any other critical health checks here

        return 0
    except Exception as e:
        logger.error(f"Health check failed with error: {str(e)}")
        return 1
