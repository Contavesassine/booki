#!/usr/bin/env python3
import os
import json
import subprocess
import sys

print("🚀 Starting Portfolio Bot...")

# Get API keys
api_key = os.getenv('KRAKEN_API_KEY')
secret_key = os.getenv('KRAKEN_SECRET_KEY')

if not api_key or not secret_key:
    print("❌ Missing API keys!")
    sys.exit(1)

print("✅ API keys loaded")

# Load and update config
with open('config_template.json', 'r') as f:
    config = json.load(f)

config['exchange']['key'] = api_key
config['exchange']['secret'] = secret_key

# Setup directories
os.makedirs('user_data/strategies', exist_ok=True)
os.makedirs('user_data/logs', exist_ok=True)

# Save config
with open('user_data/config.json', 'w') as f:
    json.dump(config, f, indent=2)

# Copy strategy
import shutil
shutil.copy('SimplePortfolio.py', 'user_data/strategies/')

print("✅ Starting freqtrade...")

# Run freqtrade directly
os.execv('/usr/local/bin/freqtrade', [
    'freqtrade', 'trade',
    '--config', 'user_data/config.json',
    '--strategy', 'SimplePortfolio',
    '--userdir', 'user_data'
])
