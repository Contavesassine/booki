#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import time

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

def main():
    logger = setup_logging()
    
    logger.info("🚀 Starting Smart Portfolio Bot...")
    logger.info("💡 Fixed Strategy Features:")
    logger.info("   - Realistic 5-15% profit targets")
    logger.info("   - Proper technical analysis")
    logger.info("   - Working DCA logic")
    logger.info("   - 8% stop loss")
    logger.info("   - 5-minute timeframe")
    
    # Get API keys
    api_key = os.getenv('KRAKEN_API_KEY')
    secret_key = os.getenv('KRAKEN_SECRET_KEY')
    
    if not api_key or not secret_key:
        logger.error("❌ Missing API keys!")
        logger.error("Set KRAKEN_API_KEY and KRAKEN_SECRET_KEY environment variables")
        sys.exit(1)
    
    logger.info(f"✅ API keys loaded: {api_key[:8]}...")
    
    # Load and update config
    try:
        with open('config_template.json', 'r') as f:
            config = json.load(f)
        
        config['exchange']['key'] = api_key
        config['exchange']['secret'] = secret_key
        
        # Setup directories
        os.makedirs('user_data/strategies', exist_ok=True)
        os.makedirs('user_data/logs', exist_ok=True)
        os.makedirs('user_data/data', exist_ok=True)
        
        # Save config
        with open('user_data/config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Configuration created")
        
        # Copy strategy
        import shutil
        shutil.copy('SimplePortfolio.py', 'user_data/strategies/')
        logger.info("✅ Strategy copied to user_data/strategies/")
        
        # Log strategy configuration
        logger.info("📊 Strategy Configuration:")
        logger.info(f"   - Max open trades: {config['max_open_trades']}")
        logger.info(f"   - Stake amount: ${config['stake_amount']}")
        logger.info(f"   - Tradable balance: {config['tradable_balance_ratio']*100}%")
        logger.info(f"   - Trading pairs: {', '.join(config['exchange']['pair_whitelist'])}")
        logger.info(f"   - Max DCA entries: {config['max_entry_position_adjustment']}")
        
        logger.info("🚀 Starting FreqTrade bot...")
        logger.info("📈 Bot will now trade automatically based on technical analysis")
        logger.info("⚠️  Monitor logs for entry/exit signals and DCA actions")
        
        # Small delay to ensure logs are written
        time.sleep(2)
        
        # Start FreqTrade
        os.execv('/usr/local/bin/freqtrade', [
            'freqtrade', 'trade',
            '--config', 'user_data/config.json',
            '--strategy', 'SimplePortfolio',
            '--userdir', 'user_data',
            '--logfile', 'user_data/logs/freqtrade.log',
            '--verbosity', '3'
        ])
        
    except FileNotFoundError as e:
        logger.error(f"❌ Configuration file not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in config: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
