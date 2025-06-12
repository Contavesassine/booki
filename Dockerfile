FROM freqtradeorg/freqtrade:stable

WORKDIR /freqtrade

# Copy files to the correct location
COPY SimplePortfolio.py ./user_data/strategies/
COPY config_template.json ./user_data/
COPY start_bot.sh ./

# Fix permissions and make executable
USER root
RUN chmod +x start_bot.sh
RUN mkdir -p user_data/logs user_data/data
RUN chown -R ftuser:ftuser user_data/

# Switch back to ftuser
USER ftuser

# Override the default entrypoint
ENTRYPOINT []
CMD ["./start_bot.sh"]
