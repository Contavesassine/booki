FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

# Copy files to current directory (not user_data)
COPY config_template.json ./
COPY SimplePortfolio.py ./
COPY start.py ./

# Fix permissions
USER root
RUN chmod +x start.py
RUN mkdir -p user_data/strategies user_data/logs user_data/data
RUN chown -R ftuser:ftuser .

# Switch back to ftuser
USER ftuser

# Start actual FreqTrade bot (NOT web server)
ENTRYPOINT []
CMD ["python", "start.py"]
