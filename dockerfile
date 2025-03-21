FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE="dark" \
    STREAMLIT_THEME_PRIMARYCOLOR="#ff4b4b" \
    STREAMLIT_PAGE_TITLE="AI DataHarvester"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for better security
RUN groupadd -r app && \
    useradd -r -g app -d /app -s /bin/bash app

# Create logs directory and set permissions
RUN mkdir -p /app/logs && \
    chown -R app:app /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create and use a healthcheck script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8501/_stcore/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Make sure all files are owned by the app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD [ "/app/healthcheck.sh" ]

# Set entry point
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]