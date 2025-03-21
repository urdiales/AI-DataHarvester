# 🌟 AI DataHarvester

An intelligent web content extraction application that uses natural language processing to transform web scraping into precise data harvesting.

## 🎯 Overview

AI DataHarvester combines the power of local LLMs (Large Language Models) with web scraping technologies to create an intelligent data extraction tool. Unlike traditional web scrapers that simply download content, this application understands what you're looking for and extracts specifically requested information using natural language queries.

## ✨ Features

### 🔍 Intelligent Web Extraction
- Extract specific information from websites using natural language
- Process and clean web content automatically
- Handle various website structures and formats

### 🧠 AI-Powered Parsing
- Use local LLMs to understand your queries
- Extract precisely what you need from web content
- Support for multiple LLM models (llama3.2, gemma, mistral, phi3, etc.)

### 🔄 Data Management
- Reset functionality to quickly start new projects
- Store extracted content in session for further processing
- View and analyze raw content before extraction

### 💾 Export Options
- Download parsed results as structured JSON files
- Send data directly to webhooks for integration with other systems
- Well-formatted data with timestamps and metadata

### 🛡️ Health Monitoring
- Real-time monitoring of system components
- Status indicators for LLM service and web scraping service
- Troubleshooting guidance and quick fixes

### 🐳 Containerization
- Docker-based deployment for consistent environment
- Multi-container setup with orchestration
- Volume persistence for logs and data

## 🚀 Getting Started

### 📋 Prerequisites

- Docker and Docker Compose
- Bright Data account credentials (for web scraping proxy)
- Internet connection

### 🔧 Installation

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

## 🎮 Usage

### 🌐 Scraping a Website
1. Enter a website URL in the input field
2. Click "Scrape Website" and wait for the process to complete
3. The content will be extracted, cleaned, and stored for parsing

### 🔎 Parsing Content
1. With scraped content loaded, enter a natural language query
   - Example: "What is the main topic of this website?"
   - Example: "Extract all product names and prices"
   - Example: "Find the author's contact information"
2. Select your preferred LLM model
3. Click "Parse Content" to extract the specific information

### 📊 Managing Results
1. View the parsed results directly in the interface
2. Download the results as a JSON file using the download button
3. Send the results to a webhook for integration with other systems
4. Reset all data when starting a new project

## 🏗️ Architecture

The application consists of two main Docker containers:

1. **ai-dataharvester**: Streamlit application for UI and web scraping
   - Handles user interactions
   - Performs web scraping via Bright Data
   - Processes and cleans content
   - Manages the parsing workflow

2. **ollama**: Local LLM service for content parsing
   - Provides inference capabilities
   - Supports multiple models
   - Performs natural language understanding
   - Extracts specific information based on queries

## 📝 Logging and Monitoring

Comprehensive logging system with files stored in the `logs/` directory:

- `scraper.log` - Web scraping operations and errors
- `parser.log` - LLM parsing activities and responses
- `streamlit.log` - UI and application flow
- `health.log` - Health check information and system status

Health monitoring is available in the sidebar of the application, providing:
- Real-time status of the Ollama LLM service
- Connection status for Bright Data service
- Troubleshooting guidance for common issues
- Manual override options for development

## 🔧 Troubleshooting

If you encounter issues:

1. Check the application logs in the `logs/` directory
2. Verify the health status in the application sidebar
3. Ensure your Bright Data credentials are correct in the `.env` file
4. Make sure the Ollama service is running with `docker-compose ps`
5. Try restarting containers with `docker-compose restart`

Common solutions:
- Reset the application data if encountering UI issues
- Check network connectivity for webhook and scraping operations
- Verify that required LLM models are downloaded in Ollama

## 🔒 Security Notes

- Application runs with non-root user in Docker for improved security
- Credentials are stored in environment variables, not hardcoded
- Webhook connections use HTTPS for secure data transmission
- Logs are segregated by component for better auditing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

[Your License Here]

## 🙏 Acknowledgments

- Streamlit for the UI framework
- Ollama for local LLM capabilities
- Bright Data for web scraping infrastructure
- Selenium for browser automation
- LangChain for LLM integration
