#!/bin/bash

echo "🚀 Setting up Portfolio Bot..."

# Check for API keys
if [ -z "$KRAKEN_API_KEY" ] || [ -z "$KRAKEN_SECRET_KEY" ]; then
    echo "❌ Missing API keys!"
    exit 1
fi

echo "✅ API keys found"

# Create config with API keys
sed "s/\"key\": \"\"/\"key\": \"$KRAKEN_API_KEY\"/" user_data/config_template.json | \
sed "s/\"secret\": \"\"/\"secret\": \"$KRAKEN_SECRET_KEY\"/" > user_data/config.json

echo "✅ Config created"

# Start freqtrade
echo "✅ Starting trading..."
freqtrade trade --config user_data/config.json --strategy SimplePortfolio --userdir user_data
