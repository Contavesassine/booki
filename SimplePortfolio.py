from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # FAST profit targets - DCA bots must take profits quickly
    minimal_roi = {
        "0": 0.08,      # 8% immediate profit target  
        "60": 0.06,     # 6% after 1 hour
        "180": 0.04,    # 4% after 3 hours
        "360": 0.03,    # 3% after 6 hours
        "720": 0.02     # 2% after 12 hours - TAKE ANY PROFIT
    }
    
    stoploss = -0.15           # Wider stop for DCA (should never hit this)
    timeframe = '5m'           
    process_only_new_candles = True
    startup_candle_count = 30
    can_short = False
    
    # AGGRESSIVE DCA but fewer total entries
    position_adjustment_enable = True
    max_entry_position_adjustment = 4  # Keep same as original
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        SIMPLE indicators for DCA signals
        """
        # RSI - simple and effective
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # EMAs for trend
        dataframe['ema_9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)
        
        # Volume for confirmation
        dataframe['volume_avg'] = dataframe['volume'].rolling(window=20).mean()
        
        # Price momentum
        dataframe['price_change'] = dataframe['close'].pct_change(periods=5) * 100
        
        # Support levels (buying opportunities)
        dataframe['low_5'] = dataframe['low'].rolling(window=5).min()
        dataframe['low_20'] = dataframe['low'].rolling(window=20).min()
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        MUCH MORE SELECTIVE buying - only on big dips
        """
        dataframe.loc[
            (
                # ONLY BUY MAJOR DIPS - be very selective
                (
                    (dataframe['rsi'] < 30) &  # Very oversold (was 45)
                    (dataframe['close'] <= dataframe['low_5'] * 1.005) &  # Very near recent low
                    (dataframe['volume'] > dataframe['volume_avg'] * 1.2) &  # Volume surge
                    (dataframe['price_change'] < -3)  # Big price drop
                )
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        TAKE PROFITS FAST - this is critical for DCA success
        """
        dataframe.loc[
            (
                # EXIT ON SMALL PROFITS - don't be greedy
                (dataframe['rsi'] > 55) &  # Not even overbought (was 75)
                (dataframe['close'] > dataframe['ema_9'])  # Above short-term trend
            ) |
            (
                # EXIT ON ANY DECENT BOUNCE
                (dataframe['price_change'] > 2) &  # Small bounce up
                (dataframe['rsi'] > 50)  # Neutral RSI
            ),
            'exit_long'] = 1
        
        return dataframe
    
    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, 
                            min_stake, max_stake, **kwargs):
        """
        AGGRESSIVE DCA - this is where DCA bots make their money
        """
        if current_profit >= -0.01:  # Only add when down 3%+ (was 1%)
            return None  
        
        # BIGGER DCA amounts - go heavy when losing
        if current_profit < -0.15:  # Down 15%+
            additional_stake = min_stake * 3.0  # Massive add (was 2.0)
            logger.info(f"🔥 MASSIVE DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.10:  # Down 10-15%
            additional_stake = min_stake * 2.5  # Big add (was 1.5)
            logger.info(f"💪 BIG DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.06:  # Down 6-10%
            additional_stake = min_stake * 2.0  # Medium add (was 1.0)
            logger.info(f"📈 MEDIUM DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.03:  # Down 3-6%
            additional_stake = min_stake * 1.0  # Small add (was 0.8)
            logger.info(f"💰 SMALL DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        else:
            return None
        
        # Check if we can still add more positions
        if trade.nr_of_successful_entries >= (self.max_entry_position_adjustment + 1):
            logger.info(f"⚠️ Max DCA entries reached for {trade.pair}")
            return None
        
        return min(additional_stake, max_stake)
    
    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          entry_tag: str, **kwargs) -> float:
        """
        MUCH SMALLER initial stakes - save money for DCA
        """
        # Use only 25% for initial entry (was 60%) - save 75% for DCA
        initial_stake = proposed_stake * 0.25
        
        logger.info(f"💰 Small initial stake for {pair}: ${initial_stake:.2f} (25% - saving for DCA)")
        
        return max(initial_stake, min_stake)
    
    def custom_exit_price(self, pair: str, trade, current_time, proposed_rate: float,
                         current_profit: float, **kwargs) -> float:
        """
        SELL IMMEDIATELY when profitable - don't wait for better prices
        """
        if current_profit > 0.02:  # If up even 2%, sell at market (was 8%)
            logger.info(f"💰 TAKING PROFIT: {pair} up {current_profit:.1%} - selling at market")
            return proposed_rate  # Take the market price immediately
        
        return proposed_rate
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """
        Log all entries for tracking
        """
        trade_value = amount * rate
        logger.info(f"🎯 DCA BUY: {pair} | {amount:.4f} @ ${rate:.4f} = ${trade_value:.2f}")
        return True
    
    def confirm_trade_exit(self, pair: str, trade, order_type: str, amount: float, 
                          rate: float, time_in_force: str, exit_reason: str, 
                          current_time, **kwargs) -> bool:
        """
        Log all exits with profit tracking
        """
        profit_pct = trade.calc_profit_ratio(rate) * 100
        profit_usd = trade.calc_profit(rate)
        
        if profit_pct > 0:
            logger.info(f"💰 DCA PROFIT: {pair} | SOLD {amount:.4f} @ ${rate:.4f} | +{profit_pct:.2f}% (+${profit_usd:.2f})")
        else:
            logger.info(f"🛑 DCA LOSS: {pair} | SOLD {amount:.4f} @ ${rate:.4f} | {profit_pct:.2f}% (${profit_usd:.2f})")
        
        logger.info(f"   Duration: {current_time - trade.open_date} | Reason: {exit_reason}")
        
        return True
    
    def leverage(self, pair: str, current_time, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str, 
                side: str, **kwargs) -> float:
        """
        Spot trading only
        """
        return 1.0
