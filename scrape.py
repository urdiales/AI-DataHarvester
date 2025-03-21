import os
from dotenv import load_dotenv
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from logger_config import setup_logger

# Set up logger for this module
logger = setup_logger(__name__, os.path.join('logs', 'scraper.log'))

# Load environment variables
load_dotenv()

# Authentication and connection details
BRIGHTDATA_USER = os.getenv("BRIGHTDATA_USER")
BRIGHTDATA_PASSWORD = os.getenv("BRIGHTDATA_PASSWORD")

if not BRIGHTDATA_USER or not BRIGHTDATA_PASSWORD:
    logger.error("Missing Bright Data credentials. Check .env file.")
    raise ValueError(
        "Missing Bright Data credentials. Ensure BRIGHTDATA_USER and BRIGHTDATA_PASSWORD are set in .env"
    )

AUTH = f"{BRIGHTDATA_USER}:{BRIGHTDATA_PASSWORD}"
SBR_WEBDRIVER = f"https://{AUTH}@brd.superproxy.io:9515"


def scrape_website(website):
    """
    Scrape website content using Selenium and Bright Data.
    
    Args:
        website: URL to scrape
        
    Returns:
        HTML content of the website
    """
    logger.info(f"Scraping website: {website}")
    
    # Validate URL format before attempting to scrape
    if not website.startswith(('http://', 'https://')):
        logger.error(f"Invalid URL format: {website}")
        raise ValueError("URL must start with http:// or https://")
    
    # Use remote connection instead of local ChromeDriver
    logger.info("Connecting to Scraping Browser...")
    
    try:
        sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")
        options = webdriver.ChromeOptions()
    except Exception as e:
        logger.error(f"Failed to initialize Chrome connection: {str(e)}")
        raise ConnectionError(f"Browser connection initialization failed: {str(e)}")

    # Create driver with remote connection
    try:
        driver = webdriver.Remote(sbr_connection, options=options)
        logger.info("Connected! Navigating...")
        
        try:
            # Navigate to the website with timeout
            driver.set_page_load_timeout(30)  # 30-second timeout
            driver.get(website)
            logger.info("Page loaded...")

            # Get the page source
            html = driver.page_source

            # Take a screenshot if needed
            logger.info("Taking page screenshot to file page.png")
            driver.get_screenshot_as_file("./page.png")

            logger.info("Navigated! Scraping page content...")

            # Wait for page to fully load with more reliability
            time.sleep(10)
            
            return html
            
        except Exception as e:
            logger.error(f"Error during page navigation or scraping: {str(e)}")
            raise
        finally:
            # Ensure driver is always closed
            logger.info("Closing WebDriver")
            driver.quit()
            
    except Exception as e:
        logger.error(f"Failed to create Remote WebDriver: {str(e)}")
        raise ConnectionError(f"Browser connection failed: {str(e)}")


def extract_body_content(html_content):
    """Extract body content from HTML"""
    logger.info("Extracting body content from HTML")
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        body_content = soup.body
        if body_content:
            logger.info("Body content extracted successfully")
            return str(body_content)
        logger.warning("No body content found in HTML")
        return ""
    except Exception as e:
        logger.error(f"Error extracting body content: {str(e)}")
        raise


def clean_body_content(body_content):
    """Clean body content by removing scripts and styles"""
    logger.info("Cleaning body content")
    try:
        soup = BeautifulSoup(body_content, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        # Get text content and clean whitespace
        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        content_length = len(cleaned_content)
        logger.info(f"Content cleaned successfully. Length: {content_length} characters")
        return cleaned_content
    except Exception as e:
        logger.error(f"Error cleaning body content: {str(e)}")
        raise


def split_dom_content(dom_content, max_length=6000):
    """Split DOM content into chunks of maximum length"""
    logger.info(f"Splitting DOM content into chunks of max {max_length} characters")
    chunks = [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks


# For direct execution
if __name__ == "__main__":
    try:
        result = scrape_website("https://example.com")
        preview = result[:500] + "..." if len(result) > 500 else result
        logger.info(f"Scraped content preview: {preview}")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
