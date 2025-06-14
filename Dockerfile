FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

# Copy configuration and strategy files
COPY config_template.json ./
COPY SimplePortfolio.py ./user_data/strategies/

# Create necessary directories
USER root
RUN mkdir -p user_data/strategies user_data/logs user_data/data
RUN chown -R ftuser:ftuser .

# Switch back to ftuser
USER ftuser

# Copy startup script
COPY start_trading.sh ./
USER root
RUN chmod +x start_trading.sh
USER ftuser

# Start actual FreqTrade bot (NOT web server)
ENTRYPOINT []
CMD ["./start_trading.sh"]
