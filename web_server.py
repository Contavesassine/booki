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
    time.sleep(5)  # Wait for web server to start
    
    print("🚀 Starting Freqtrade...")
    
    # Get API keys
    api_key = os.getenv('KRAKEN_API_KEY')
    secret_key = os.getenv('KRAKEN_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Missing API keys!")
        return
    
    # Load and update config
    with open('user_data/config_template.json', 'r') as f:
        config = json.load(f)
    
    config['exchange']['key'] = api_key
    config['exchange']['secret'] = secret_key
    
    # Create directories
    os.makedirs('user_data/strategies', exist_ok=True)
    os.makedirs('user_data/logs', exist_ok=True)
    
    # Save config
    with open('user_data/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Copy strategy
    import shutil
    shutil.copy('SimplePortfolio.py', 'user_data/strategies/')
    
    print("✅ Starting accumulation trading...")
    
    # Start freqtrade
    subprocess.run([
        'freqtrade', 'trade',
        '--config', 'user_data/config.json',
        '--strategy', 'SimplePortfolio',
        '--userdir', 'user_data'
    ])

def main():
    # Start freqtrade in background
    bot_thread = threading.Thread(target=start_freqtrade, daemon=True)
    bot_thread.start()
    
    # Start web server for Railway
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    
    print(f"🌐 Web server starting on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    main()
