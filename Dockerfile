FROM freqtradeorg/freqtrade:stable

# Switch to root to install packages
USER root

# Copy our files
COPY . /freqtrade/
WORKDIR /freqtrade

# Install any additional requirements
RUN pip install --no-cache-dir -r requirements.txt

# Make start script executable
RUN chmod +x start.py

# Create directories
RUN mkdir -p user_data/strategies user_data/logs user_data/data

# Switch back to freqtrade user
USER ftuser

# Run our start script
CMD ["python", "start.py"]
