# AI DataHarvester

An intelligent web content extraction application that uses Streamlit for the UI, Selenium for web scraping, and Ollama for LLM-based content parsing.

## Features

- Intelligent web content extraction
- Natural language parsing with LLMs
- Content cleaning and processing
- Comprehensive logging and health monitoring
- Docker containerization for easy deployment
- JSON export functionality

## Setup

### Prerequisites

- Docker and Docker Compose
- Bright Data account credentials
- Internet connection

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/ai-dataharvester.git
   cd ai-dataharvester
   ```

2. Run the setup script to create necessary directories:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Edit the `.env` file with your Bright Data credentials:

   ```
   BRIGHTDATA_USER=your_brightdata_user
   BRIGHTDATA_PASSWORD=your_brightdata_password
   ```

4. Build and start the containers:

   ```bash
   docker-compose up -d
   ```

5. Access the application at http://localhost:8501

## Usage

1. Enter a website URL and click "Scrape Website"
2. Once the content is scraped, describe what you want to extract
3. Select an LLM model from the dropdown
4. Click "Parse Content" to extract the information
5. Use the download button to save results as JSON
6. Reset the application when needed using the reset button

## Architecture

The application consists of two main Docker containers:

1. **ai-dataharvester**: Streamlit application for UI and web scraping
2. **ollama**: Local LLM service for content parsing

## Logging and Monitoring

Logs are stored in the `logs/` directory and are accessible both from the host and within the containers. They include:

- `scraper.log` - Web scraping operations
- `parser.log` - LLM parsing operations
- `streamlit.log` - UI and application operations
- `health.log` - Health check information

Health monitoring is available in the sidebar of the application.

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Verify the health status in the application sidebar
3. Ensure your Bright Data credentials are correct in the `.env` file
4. Make sure the Ollama service is running by checking `docker-compose ps`

## License

[Your License Here]
