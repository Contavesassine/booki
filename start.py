#!/usr/bin/env python3
import os
import json
import subprocess
import sys

print("🚀 Starting Portfolio Bot on Railway...")

# Get API keys from environment
api_key = os.getenv('KRAKEN_API_KEY')
secret_key = os.getenv('KRAKEN_SECRET_KEY')

if not api_key or not secret_key:
    print("❌ Missing API keys in environment variables!")
    print("Make sure KRAKEN_API_KEY and KRAKEN_SECRET_KEY are set in Railway")
    sys.exit(1)

print("✅ API keys found")

# Load config template
try:
    with open('config_template.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("❌ config_template.json not found!")
    sys.exit(1)

# Set API keys
config['exchange']['key'] = api_key
config['exchange']['secret'] = secret_key

# Create user_data structure
os.makedirs('user_data/strategies', exist_ok=True)
os.makedirs('user_data/logs', exist_ok=True)
os.makedirs('user_data/data', exist_ok=True)

# Save runtime config
with open('user_data/config.json', 'w') as f:
    json.dump(config, f, indent=2)

# Copy strategy file
try:
    import shutil
    shutil.copy('SimplePortfolio.py', 'user_data/strategies/SimplePortfolio.py')
    print("✅ Strategy file copied")
except FileNotFoundError:
    print("❌ SimplePortfolio.py not found!")
    sys.exit(1)

print("✅ Starting live trading...")

# Start freqtrade
subprocess.run([
    'freqtrade', 'trade',
    '--config', 'user_data/config.json',
    '--strategy', 'SimplePortfolio',
    '--userdir', 'user_data'
])
