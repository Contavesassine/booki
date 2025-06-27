from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # FAST profit targets
    minimal_roi = {
        "0": 0.08,      # 8% immediate profit target  
        "60": 0.06,     # 6% after 1 hour
        "180": 0.04,    # 4% after 3 hours
        "360": 0.03,    # 3% after 6 hours
        "720": 0.02     # 2% after 12 hours
    }
    
    stoploss = -0.15           
    timeframe = '5m'           
    process_only_new_candles = True
    startup_candle_count = 30
    can_short = False
    
    position_adjustment_enable = True
    max_entry_position_adjustment = 8
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Basic indicators"""
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['volume_avg'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['price_change'] = dataframe['close'].pct_change(periods=5) * 100
        dataframe['low_5'] = dataframe['low'].rolling(window=5).min()
        dataframe['low_20'] = dataframe['low'].rolling(window=20).min()
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        🚨 NUCLEAR OPTION - ALWAYS BUY TO TEST DCA SYSTEM
        """
        pair = metadata['pair']
        current_price = dataframe['close'].iloc[-1]
        rsi_current = dataframe['rsi'].iloc[-1]
        
        # 🚨 IMPOSSIBLE TO MISS LOG MESSAGES
        logger.info(f"🚨🚨🚨 NUCLEAR ENTRY CHECK: {pair} @ ${current_price:.4f} | RSI: {rsi_current:.1f}")
        logger.info(f"🚨🚨🚨 ALWAYS BUYING: Setting enter_long=1 for {pair}")
        logger.info(f"🚨🚨🚨 THIS MESSAGE PROVES STRATEGY UPDATE WORKED!")
        
        # ALWAYS BUY - NO CONDITIONS WHATSOEVER
        dataframe.loc[:, 'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Take profits fast"""
        dataframe.loc[
            (
                (dataframe['rsi'] > 55) &
                (dataframe['close'] > dataframe['ema_9'])
            ) |
            (
                (dataframe['price_change'] > 2) &
                (dataframe['rsi'] > 50)
            ),
            'exit_long'] = 1
        
        return dataframe
    
    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, 
                            min_stake, max_stake, **kwargs):
        """
        🚨 NUCLEAR DCA - WITH IMPOSSIBLE TO MISS LOGGING
        """
        # 🚨 SUPER OBVIOUS DEBUG LOGS
        logger.info(f"🚨🚨🚨 DCA CHECK: {trade.pair} | Profit: {current_profit:.2%} | Entries: {trade.nr_of_successful_entries}")
        logger.info(f"🚨🚨🚨 Trade Details: Amount: {trade.amount} | Open: ${trade.open_rate:.4f} | Current: ${current_rate:.4f}")
        
        if current_profit >= -0.01:  # DCA when down 1%+
            logger.info(f"🚨🚨🚨 No DCA: {trade.pair} not down enough ({current_profit:.2%} vs -1% threshold)")
            return None
        
        # DCA amounts
        if current_profit < -0.15:
            additional_stake = min_stake * 3.0
            logger.info(f"🚨🚨🚨 MASSIVE DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.10:
            additional_stake = min_stake * 2.5
            logger.info(f"🚨🚨🚨 BIG DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.06:
            additional_stake = min_stake * 2.0
            logger.info(f"🚨🚨🚨 MEDIUM DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.01:
            additional_stake = min_stake * 1.0
            logger.info(f"🚨🚨🚨 SMALL DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        else:
            return None
        
        if trade.nr_of_successful_entries >= (self.max_entry_position_adjustment + 1):
            logger.info(f"🚨🚨🚨 Max DCA entries reached for {trade.pair}")
            return None
        
        return min(additional_stake, max_stake)
    
    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          entry_tag: str, **kwargs) -> float:
        """TINY stakes for testing"""
        initial_stake = proposed_stake * 0.05  # 5% only
        
        logger.info(f"🚨🚨🚨 TINY stake for {pair}: ${initial_stake:.2f} (5% - saving 95% for DCA)")
        
        return max(initial_stake, min_stake)
    
    def custom_exit_price(self, pair: str, trade, current_time, proposed_rate: float,
                         current_profit: float, **kwargs) -> float:
        """Sell when profitable"""
        if current_profit > 0.02:
            logger.info(f"🚨🚨🚨 TAKING PROFIT: {pair} up {current_profit:.1%} - selling at market")
            return proposed_rate
        
        return proposed_rate
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """Log entries"""
        trade_value = amount * rate
        logger.info(f"🚨🚨🚨 NUCLEAR BUY: {pair} | {amount:.4f} @ ${rate:.4f} = ${trade_value:.2f}")
        return True
    
    def confirm_trade_exit(self, pair: str, trade, order_type: str, amount: float, 
                          rate: float, time_in_force: str, exit_reason: str, 
                          current_time, **kwargs) -> bool:
        """Log exits"""
        profit_pct = trade.calc_profit_ratio(rate) * 100
        profit_usd = trade.calc_profit(rate)
        
        if profit_pct > 0:
            logger.info(f"🚨🚨🚨 NUCLEAR PROFIT: {pair} | SOLD {amount:.4f} @ ${rate:.4f} | +{profit_pct:.2f}% (+${profit_usd:.2f})")
        else:
            logger.info(f"🚨🚨🚨 NUCLEAR LOSS: {pair} | SOLD {amount:.4f} @ ${rate:.4f} | {profit_pct:.2f}% (${profit_usd:.2f})")
        
        return True
    
    def leverage(self, pair: str, current_time, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str, 
                side: str, **kwargs) -> float:
        """Spot trading only"""
        return 1.0
