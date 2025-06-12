#!/bin/bash
set -e

echo "🚀 Starting Portfolio Bot..."

# Check API keys
if [ -z "$KRAKEN_API_KEY" ] || [ -z "$KRAKEN_SECRET_KEY" ]; then
    echo "❌ Missing API keys!"
    echo "Set KRAKEN_API_KEY and KRAKEN_SECRET_KEY in Railway environment"
    exit 1
fi

echo "✅ API keys found"

# Create config with API keys using sed
sed -e "s|\"key\": \"\"|\"key\": \"$KRAKEN_API_KEY\"|g" \
    -e "s|\"secret\": \"\"|\"secret\": \"$KRAKEN_SECRET_KEY\"|g" \
    user_data/config_template.json > user_data/config.json

echo "✅ Config created"

# Verify files exist
if [ ! -f user_data/strategies/SimplePortfolio.py ]; then
    echo "❌ Strategy file missing!"
    exit 1
fi

if [ ! -f user_data/config.json ]; then
    echo "❌ Config file missing!"
    exit 1
fi

echo "✅ All files ready"
echo "✅ Starting freqtrade..."

# Start freqtrade
exec freqtrade trade \
    --config user_data/config.json \
    --strategy SimplePortfolio \
    --userdir user_data
