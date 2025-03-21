#!/bin/bash

# Create necessary directories
mkdir -p logs

# Set appropriate permissions
chmod 755 logs

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating sample .env file..."
    cat > .env << EOF
# Bright Data Credentials
BRIGHTDATA_USER=your_brightdata_user
BRIGHTDATA_PASSWORD=your_brightdata_password
EOF
    echo "Please update the .env file with your actual credentials"
fi

# Create empty log files with appropriate permissions
touch logs/scraper.log logs/parser.log logs/streamlit.log logs/health.log
chmod 644 logs/*.log

echo "Setup complete. Directory structure created."
