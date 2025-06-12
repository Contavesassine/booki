FROM freqtradeorg/freqtrade:stable

# Copy our files
COPY . /freqtrade/
WORKDIR /freqtrade

# Make start script executable
RUN chmod +x start.py

# Create directories
RUN mkdir -p user_data/strategies user_data/logs user_data/data

# Use python directly instead of the freqtrade entrypoint
ENTRYPOINT []
CMD ["python", "start.py"]
