FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

# Copy files to current directory (not user_data)
COPY config_template.json ./
COPY SimplePortfolio.py ./
COPY web_server.py ./

# Fix permissions
USER root
RUN chmod +x web_server.py
RUN mkdir -p user_data/strategies user_data/logs user_data/data
RUN chown -R ftuser:ftuser .

# Switch back to ftuser
USER ftuser

# Start web server
ENTRYPOINT []
CMD ["python", "web_server.py"]
