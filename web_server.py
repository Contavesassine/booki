#!/usr/bin/env python3
import os
import json
import subprocess
import threading
import time
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🚀 Starting Portfolio Bot Web Server...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print("Files in directory:")
for f in os.listdir('.'):
    print(f"  - {f}")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/health' or self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                
                status = "✅ Portfolio Bot Web Server Running\n"
                status += f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                status += "Bot Status: Trading ONDO/USD and CPOOL/USD\n"
                
                self.wfile.write(status.encode())
                print(f"✅ Health check served at {time.strftime('%H:%M:%S')}")
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"❌ Error in health handler: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP access logs

def start_freqtrade():
    """Start freqtrade in a separate thread"""
    try:
        print("🤖 Starting Freqtrade thread...")
        time.sleep(5)  # Wait for web server to start
        
        # Check API keys
        api_key = os.getenv('KRAKEN_API_KEY')
        secret_key = os.getenv('KRAKEN_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("❌ Missing API keys!")
            return
        
        print("✅ API keys found")
        
        # Check if config file exists
        if not os.path.exists('user_data/config_template.json'):
            print("❌ config_template.json not found!")
            print("Files in user_data:")
            if os.path.exists('user_data'):
                for f in os.listdir('user_data'):
                    print(f"  - {f}")
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
        
        print("✅ Config created")
        
        # Copy strategy
        if os.path.exists('SimplePortfolio.py'):
            import shutil
            shutil.copy('SimplePortfolio.py', 'user_data/strategies/')
            print("✅ Strategy copied")
        else:
            print("❌ SimplePortfolio.py not found!")
            return
        
        print("🚀 Starting freqtrade...")
        
        # Start freqtrade
        result = subprocess.run([
            'freqtrade', 'trade',
            '--config', 'user_data/config.json',
            '--strategy', 'SimplePortfolio',
            '--userdir', 'user_data'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Freqtrade failed: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Error in freqtrade thread: {e}")

def main():
    try:
        print("🌐 Starting web server...")
        
        # Get port from environment
        port = int(os.getenv('PORT', 8080))
        print(f"📡 Using port: {port}")
        
        # Start freqtrade in background thread
        bot_thread = threading.Thread(target=start_freqtrade, daemon=True)
        bot_thread.start()
        print("🤖 Bot thread started")
        
        # Start web server
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"✅ Web server ready on 0.0.0.0:{port}")
        
        # Test server locally
        print("🔍 Testing health endpoint...")
        
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
