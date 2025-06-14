FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

# Copy configuration and strategy files
COPY config_template.json ./
COPY SimplePortfolio.py ./
COPY start.py ./

# Install additional dependencies if needed
USER root

# Create directory structure and set permissions
RUN mkdir -p user_data/strategies user_data/logs user_data/data && \
    chmod +x start.py && \
    chown -R ftuser:ftuser .

# Switch back to ftuser for security
USER ftuser

# Healthcheck to ensure bot is running
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD freqtrade show-config --config user_data/config.json || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FREQTRADE_USERDIR=/freqtrade/user_data

# Start the enhanced bot
ENTRYPOINT []
CMD ["python", "start.py"]
