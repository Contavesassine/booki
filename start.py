#!/usr/bin/env python3
import os
import json
import subprocess
import sys

print("🚀 Starting Portfolio Bot...")

# Get API keys from Railway environment
api_key = os.getenv('KRAKEN_API_KEY')
secret_key = os.getenv('KRAKEN_SECRET_KEY')

if not api_key or not secret_key:
    print("❌ Missing API keys in environment!")
    sys.exit(1)

print("✅ API keys loaded")

# Load config template
with open('config_template.json', 'r') as f:
    config = json.load(f)

# Set API keys
config['exchange']['key'] = api_key
config['exchange']['secret'] = secret_key

# Create directory structure
os.makedirs('user_data/strategies', exist_ok=True)
os.makedirs('user_data/logs', exist_ok=True)

# Save runtime config
with open('user_data/config.json', 'w') as f:
    json.dump(config, f, indent=2)

# Copy strategy file
import shutil
shutil.copy('SimplePortfolio.py', 'user_data/strategies/')

print("✅ Configuration ready, starting trading...")

# Start freqtrade
subprocess.run([
    'freqtrade', 'trade',
    '--config', 'user_data/config.json',
    '--strategy', 'SimplePortfolio', 
    '--userdir', 'user_data'
])
