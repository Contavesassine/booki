#!/usr/bin/env python3
import os
import json
import subprocess
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Accumulator Bot is running and trading!")
    
    def log_message(self, format, *args):
        pass

def start_freqtrade():
    """Start freqtrade in background"""
    time.sleep(5)
    
    print("🚀 Starting Freqtrade...")
    print(f"Working directory: {os.getcwd()}")
    print("Files available:")
    for f in os.listdir('.'):
        print(f"  - {f}")
    
    # Get API keys
    api_key = os.getenv('KRAKEN_API_KEY')
    secret_key = os.getenv('KRAKEN_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Missing API keys!")
        return
    
    print("✅ API keys found")
    
    # Find config file (it should be in current directory, not user_data)
    config_file = 'config_template.json'
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found!")
        return
    
    # Load and update config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    config['exchange']['key'] = api_key
    config['exchange']['secret'] = secret_key
    
    # Create directories
    os.makedirs('user_data/strategies', exist_ok=True)
    os.makedirs('user_data/logs', exist_ok=True)
    
    # Save runtime config
    with open('user_data/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Config created")
    
    # Copy strategy
    if os.path.exists('SimplePortfolio.py'):
        import shutil
        shutil.copy('SimplePortfolio.py', 'user_data/strategies/')
        print("✅ Strategy copied")
    else:
        print("❌ SimplePortfolio.py not found!")
        return
    
    print("✅ Starting accumulation trading...")
    
    # Start freqtrade
    subprocess.run([
        'freqtrade', 'trade',
        '--config', 'user_data/config.json',
        '--strategy', 'SimplePortfolio',
        '--userdir', 'user_data'
    ])

def main():
    print("🌐 Starting Accumulator Bot Web Server...")
    
    # Start freqtrade in background
    bot_thread = threading.Thread(target=start_freqtrade, daemon=True)
    bot_thread.start()
    
    # Start web server for Railway
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    
    print(f"🌐 Web server ready on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
