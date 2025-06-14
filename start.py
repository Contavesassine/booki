#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import time
import shutil

def setup_logging():
    """Setup comprehensive logging"""
    import logging
    
    # Create logs directory
    os.makedirs('user_data/logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('user_data/logs/bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    return logger

def get_config_template():
    """Return the config template as a dict - no file needed"""
    return {
        "$schema": "https://schema.freqtrade.io/schema.json",
        "max_open_trades": 4,
        "stake_currency": "USD",
        "stake_amount": 5,
        "tradable_balance_ratio": 0.90,
        "fiat_display_currency": "USD",
        "dry_run": False,
        "cancel_open_orders_on_exit": True,
        "trading_mode": "spot",
        "unfilledtimeout": {
            "entry": 15,
            "exit": 15,
            "exit_timeout_count": 3,
            "unit": "minutes"
        },
        "entry_pricing": {
            "price_side": "other",
            "use_order_book": True,
            "order_book_top": 1,
            "price_last_balance": 0.0,
            "check_depth_of_market": {
                "enabled": False,
                "bids_to_ask_delta": 1
            }
        },
        "exit_pricing": {
            "price_side": "other",
            "use_order_book": True,
            "order_book_top": 1
        },
        "exchange": {
            "name": "kraken",
            "key": "",
            "secret": "",
            "ccxt_config": {
                "enableRateLimit": True,
                "rateLimit": 2000,
                "sandbox": False
            },
            "pair_whitelist": [
                "ONDO/USD",
                "CPOOL/USD"
            ],
            "pair_blacklist": []
        },
        "pairlists": [
            {
                "method": "StaticPairList"
            }
        ],
        "telegram": {
            "enabled": False,
            "token": "",
            "chat_id": ""
        },
        "api_server": {
            "enabled": True,
            "listen_ip_address": "127.0.0.1",
            "listen_port": 8080,
            "username": "freqtrader",
            "password": "freqtrader123",
            "jwt_secret_key": "supersecretkey123",
            "CORS_origins": [],
            "verbosity": "info"
        },
        "bot_name": "SmartPortfolioBot",
        "initial_state": "running",
        "force_entry_enable": False,
        "internals": {
            "process_throttle_secs": 5
        },
        "dataformat_ohlcv": "json",
        "dataformat_trades": "jsongz",
        "position_adjustment_enable": True,
        "max_entry_position_adjustment": 3
    }

def find_freqtrade_path():
    """Find the correct path to freqtrade executable"""
    # Try common paths
    possible_paths = [
        '/usr/local/bin/freqtrade',
        '/usr/bin/freqtrade',
        '/bin/freqtrade',
        'freqtrade'  # This will use PATH
    ]
    
    for path in possible_paths:
        if path == 'freqtrade':
            # Use shutil.which to find in PATH
            found_path = shutil.which('freqtrade')
            if found_path:
                return found_path
        else:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
    
    return None

def main():
    logger = setup_logging()
    
    logger.info("🚀 Starting Smart Portfolio Bot...")
    logger.info("💡 Fixed Strategy Features:")
    logger.info("   - Fast 2-8% profit targets (DCA style)")
    logger.info("   - Selective entry signals")
    logger.info("   - Heavy DCA when losing")
    logger.info("   - Small initial stakes")
    logger.info("   - 5-minute timeframe")
    
    # Get API keys
    api_key = os.getenv('KRAKEN_API_KEY')
    secret_key = os.getenv('KRAKEN_SECRET_KEY')
    
    if not api_key or not secret_key:
        logger.error("❌ Missing API keys!")
        logger.error("Set KRAKEN_API_KEY and KRAKEN_SECRET_KEY environment variables")
        sys.exit(1)
    
    logger.info(f"✅ API keys loaded: {api_key[:8]}...")
    
    # Find freqtrade executable
    freqtrade_path = find_freqtrade_path()
    if not freqtrade_path:
        logger.error("❌ Could not find freqtrade executable!")
        sys.exit(1)
    
    logger.info(f"✅ Found freqtrade at: {freqtrade_path}")
    
    # Load config from embedded template - NO FILE READING
    try:
        config = get_config_template()
        
        config['exchange']['key'] = api_key
        config['exchange']['secret'] = secret_key
        
        # Setup directories
        os.makedirs('user_data/strategies', exist_ok=True)
        os.makedirs('user_data/logs', exist_ok=True)
        os.makedirs('user_data/data', exist_ok=True)
        
        # Save config
        with open('user_data/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Configuration created from embedded template")
        
        # Copy strategy
        if os.path.exists('SimplePortfolio.py'):
            shutil.copy('SimplePortfolio.py', 'user_data/strategies/')
            logger.info("✅ Strategy copied to user_data/strategies/")
        else:
            logger.error("❌ SimplePortfolio.py not found!")
            sys.exit(1)
        
        # Log strategy configuration
        logger.info("📊 Strategy Configuration:")
        logger.info(f"   - Max open trades: {config['max_open_trades']}")
        logger.info(f"   - Stake amount: ${config['stake_amount']}")
        logger.info(f"   - Tradable balance: {config['tradable_balance_ratio']*100}%")
        logger.info(f"   - Trading pairs: {', '.join(config['exchange']['pair_whitelist'])}")
        logger.info(f"   - Max DCA entries: {config['max_entry_position_adjustment']}")
        
        logger.info("🚀 Starting FreqTrade bot...")
        logger.info("📈 Bot will now trade with profit-focused DCA strategy")
        logger.info("⚠️  Monitor logs for entry/exit signals and DCA actions")
        
        # Small delay to ensure logs are written
        time.sleep(2)
        
        # FIXED COMMAND - removed invalid --verbosity argument
        cmd = [
            'freqtrade', 'trade',
            '--config', 'user_data/config.json',
            '--strategy', 'SimplePortfolio',
            '--userdir', 'user_data',
            '--logfile', 'user_data/logs/freqtrade.log',
            '-vvv'  # Use valid verbose flag instead of --verbosity 3
        ]
        
        logger.info(f"🎯 Executing command: {' '.join(cmd)}")
        
        # Use subprocess.run instead of os.execv for better error handling
        result = subprocess.run(cmd, check=False)
        
        if result.returncode != 0:
            logger.error(f"❌ FreqTrade exited with code: {result.returncode}")
            sys.exit(result.returncode)
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
