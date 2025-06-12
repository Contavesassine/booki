FROM freqtradeorg/freqtrade:stable

# Copy files
COPY SimplePortfolio.py /freqtrade/user_data/strategies/
COPY config_template.json /freqtrade/user_data/config_template.json
COPY setup_and_run.sh /freqtrade/

# Make script executable
RUN chmod +x setup_and_run.sh

WORKDIR /freqtrade

CMD ["./setup_and_run.sh"]
