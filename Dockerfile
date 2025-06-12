FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

# Copy ALL files to the container
COPY . .

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
