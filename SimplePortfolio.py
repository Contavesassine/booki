from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # AGGRESSIVE profit targets - hold for real gains
    minimal_roi = {
        "0": 0.25,      # 25% max profit (let winners run)
        "180": 0.15,    # 15% after 3 hours
        "720": 0.10,    # 10% after 12 hours  
        "1440": 0.05,   # 5% after 1 day
        "2880": 0.03    # 3% after 2 days
    }
    
    stoploss = -0.12           # Wider 12% stop loss (give trades room)
    timeframe = '5m'           
    process_only_new_candles = True
    startup_candle_count = 30
    can_short = False
    
    # AGGRESSIVE position management
    position_adjustment_enable = True
    max_entry_position_adjustment = 4  # Max 4 additional buys (5 total entries)
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        SIMPLE indicators that actually work
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
        AGGRESSIVE buying - catch dips and trends
        """
        dataframe.loc[
            (
                # BUY THE DIP CONDITIONS
                (
                    (dataframe['rsi'] < 45) &  # RSI oversold/neutral
                    (dataframe['close'] <= dataframe['low_5'] * 1.02) &  # Near recent low
                    (dataframe['volume'] > dataframe['volume_avg'] * 0.5)  # Some volume
                ) |
                # TREND FOLLOWING CONDITIONS  
                (
                    (dataframe['ema_9'] > dataframe['ema_21']) &  # Short uptrend
                    (dataframe['rsi'] > 35) & (dataframe['rsi'] < 65) &  # Not extreme
                    (dataframe['close'] > dataframe['close'].shift(1))  # Price rising
                ) |
                # MOMENTUM BREAKOUT CONDITIONS
                (
                    (dataframe['price_change'] > 2) &  # Strong 5-candle momentum
                    (dataframe['rsi'] < 70) &  # Not overbought
                    (dataframe['volume'] > dataframe['volume_avg'] * 1.2)  # Volume surge
                )
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        HOLD FOR PROFITS - only exit on clear weakness
        """
        dataframe.loc[
            (
                # OVERBOUGHT AND WEAKENING
                (dataframe['rsi'] > 75) &  # Very overbought
                (dataframe['ema_9'] < dataframe['ema_9'].shift(1)) &  # EMA turning down
                (dataframe['close'] < dataframe['close'].shift(2))  # Price weakening
            ) |
            (
                # CLEAR TREND REVERSAL
                (dataframe['ema_9'] < dataframe['ema_21']) &  # Trend broken
                (dataframe['rsi'] < 45) &  # Momentum weak
                (dataframe['price_change'] < -3)  # Strong down move
            ),
            'exit_long'] = 1
        
        return dataframe
    
    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, 
                            min_stake, max_stake, **kwargs):
        """
        AGGRESSIVE DCA - double down on losers
        """
        if current_profit >= -0.01:  # Only add when down 1%+
            return None  
        
        # Calculate how much to add based on loss
        if current_profit < -0.08:  # Down 8%+
            additional_stake = min_stake * 2.0  # Big add
            logger.info(f"🔥 HEAVY BUY: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.05:  # Down 5-8%
            additional_stake = min_stake * 1.5  # Medium add
            logger.info(f"💪 STRONG BUY: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.03:  # Down 3-5%
            additional_stake = min_stake * 1.0  # Normal add
            logger.info(f"📈 BUY DIP: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.01:  # Down 1-3%
            additional_stake = min_stake * 0.8  # Small add
            logger.info(f"💰 Small add: ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        else:
            return None
        
        # Check if we can still add more positions
        if trade.nr_of_successful_entries >= (self.max_entry_position_adjustment + 1):
            logger.info(f"⚠️ Max positions reached for {trade.pair}")
            return None
        
        return min(additional_stake, max_stake)
    
    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          entry_tag: str, **kwargs) -> float:
        """
        SMALLER initial stakes to leave room for averaging
        """
        # Use 60% of proposed stake for initial entry (leave room for DCA)
        initial_stake = proposed_stake * 0.6
        
        logger.info(f"💰 Initial stake for {pair}: ${initial_stake:.2f} (60% of max)")
        
        return max(initial_stake, min_stake)
    
    def custom_exit_price(self, pair: str, trade, current_time, proposed_rate: float,
                         current_profit: float, **kwargs) -> float:
        """
        Try to get better exit prices when profitable
        """
        if current_profit > 0.08:  # If up 8%+, try for slightly better price
            better_price = proposed_rate * 1.002  # 0.2% above market
            logger.info(f"💎 Aiming higher: ${better_price:.4f} vs market ${proposed_rate:.4f}")
            return better_price
        
        return proposed_rate
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """
        Log all entries for tracking
        """
        trade_value = amount * rate
        logger.info(f"🎯 BUY: {pair} | {amount:.4f} @ ${rate:.4f} = ${trade_value:.2f}")
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
            logger.info(f"🚀 PROFIT: {pair} | {amount:.4f} @ ${rate:.4f} | +{profit_pct:.2f}% (+${profit_usd:.2f})")
        else:
            logger.info(f"🛑 LOSS: {pair} | {amount:.4f} @ ${rate:.4f} | {profit_pct:.2f}% (${profit_usd:.2f})")
        
        logger.info(f"   Duration: {current_time - trade.open_date} | Reason: {exit_reason}")
        
        return True
    
    def leverage(self, pair: str, current_time, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str, 
                side: str, **kwargs) -> float:
        """
        Spot trading only
        """
        return 1.0
