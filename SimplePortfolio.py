from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import logging
import numpy as np

logger = logging.getLogger(__name__)

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # REALISTIC profit targets - not delusional 30%
    minimal_roi = {
        "0": 0.15,      # 15% max profit target
        "60": 0.08,     # 8% after 1 hour
        "180": 0.05,    # 5% after 3 hours  
        "360": 0.03,    # 3% after 6 hours
        "720": 0.02     # 2% after 12 hours
    }
    
    stoploss = -0.08           # Tighter 8% stop loss
    timeframe = '5m'           # More responsive 5min candles
    process_only_new_candles = True
    startup_candle_count = 50
    can_short = False
    
    # Position management
    position_adjustment_enable = True
    max_entry_position_adjustment = 3  # Max 3 additional buys (4 total entries)
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        ACTUAL technical analysis indicators - not random shit
        """
        # RSI for oversold/overbought
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_smooth'] = ta.EMA(dataframe['rsi'], timeperiod=5)
        
        # Multiple EMAs for trend analysis
        dataframe['ema_8'] = ta.EMA(dataframe, timeperiod=8)
        dataframe['ema_21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        
        # MACD for momentum
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']
        
        # Bollinger Bands for volatility
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        # Volume analysis
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # Support/Resistance levels
        dataframe['support'] = dataframe['low'].rolling(window=20).min()
        dataframe['resistance'] = dataframe['high'].rolling(window=20).max()
        
        # Trend strength
        dataframe['trend_strength'] = (dataframe['ema_8'] - dataframe['ema_50']) / dataframe['ema_50'] * 100
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        SMART entry conditions - wait for actual opportunities
        """
        dataframe.loc[
            (
                # TREND CONDITIONS (must be in uptrend)
                (dataframe['ema_8'] > dataframe['ema_21']) &  # Short term up
                (dataframe['ema_21'] > dataframe['ema_50']) &  # Medium term up
                (dataframe['trend_strength'] > -2) &  # Not in severe downtrend
                
                # OVERSOLD CONDITIONS (buy the dip)
                (dataframe['rsi'] < 40) &  # RSI oversold
                (dataframe['rsi'] > 25) &  # But not extremely oversold
                (dataframe['bb_percent'] < 0.3) &  # Near lower BB
                
                # MOMENTUM CONDITIONS (confirming reversal)
                (dataframe['macd_hist'] > dataframe['macd_hist'].shift(1)) &  # MACD improving
                (dataframe['close'] > dataframe['support'] * 1.005) &  # Above support
                
                # VOLUME CONDITIONS (institutional interest)
                (dataframe['volume_ratio'] > 0.8) &  # Decent volume
                (dataframe['volume_ratio'] < 3.0) &  # Not panic selling
                
                # PRICE ACTION CONDITIONS
                (dataframe['close'] > dataframe['open']) |  # Green candle OR
                (dataframe['close'] > dataframe['close'].shift(1))  # Higher close
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        TAKE PROFITS - don't be greedy
        """
        dataframe.loc[
            (
                # OVERBOUGHT CONDITIONS
                (dataframe['rsi'] > 70) &  # RSI overbought
                (dataframe['bb_percent'] > 0.8) &  # Near upper BB
                
                # MOMENTUM WEAKENING
                (dataframe['macd_hist'] < dataframe['macd_hist'].shift(1)) &  # MACD weakening
                (dataframe['close'] < dataframe['resistance'] * 0.995) &  # Below resistance
                
                # PROFIT TAKING
                (dataframe['close'] > dataframe['ema_8'] * 1.03)  # 3% above EMA
            ) |
            (
                # TREND REVERSAL
                (dataframe['ema_8'] < dataframe['ema_21']) &  # Short term trend broken
                (dataframe['rsi'] < 50) &  # RSI below midline
                (dataframe['macd'] < dataframe['macd_signal'])  # MACD bearish
            ),
            'exit_long'] = 1
        
        return dataframe
    
    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, 
                            min_stake, max_stake, **kwargs):
        """
        WORKING DCA logic - actually add to losing positions
        """
        if current_profit >= 0:
            return None  # Don't add to winning positions
        
        # Calculate additional stake based on loss severity
        if current_profit < -0.06:  # Down 6%+
            additional_stake = min_stake * 1.5  # Larger add
            logger.info(f"🔥 HEAVY DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.04:  # Down 4-6%
            additional_stake = min_stake * 1.0  # Normal add
            logger.info(f"📈 DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        elif current_profit < -0.02:  # Down 2-4%
            additional_stake = min_stake * 0.7  # Small add
            logger.info(f"💰 Small DCA: Adding ${additional_stake:.2f} to {trade.pair} (down {current_profit:.1%})")
        else:
            return None  # Don't add yet
        
        # Ensure we have enough adjustments left
        if trade.nr_of_successful_entries >= (self.max_entry_position_adjustment + 1):
            logger.info(f"⚠️ Max entries reached for {trade.pair}")
            return None
        
        return min(additional_stake, max_stake)
    
    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          entry_tag: str, **kwargs) -> float:
        """
        Smart position sizing based on market conditions
        """
        # Use 80% of configured stake for initial entries
        initial_stake = proposed_stake * 0.8
        
        logger.info(f"💰 Initial stake for {pair}: ${initial_stake:.2f}")
        
        return max(initial_stake, min_stake)
    
    def custom_exit_price(self, pair: str, trade, current_time, proposed_rate: float,
                         current_profit: float, **kwargs) -> float:
        """
        Smart exit pricing - don't leave money on the table
        """
        if current_profit > 0.05:  # If up 5%+, try to get better price
            better_price = proposed_rate * 1.001  # 0.1% above market
            logger.info(f"💎 Aiming for better exit price: ${better_price:.4f} vs ${proposed_rate:.4f}")
            return better_price
        
        return proposed_rate
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """
        Final entry confirmation with detailed logging
        """
        trade_value = amount * rate
        logger.info(f"🎯 ENTRY CONFIRMED: {pair}")
        logger.info(f"   Amount: {amount:.4f} @ ${rate:.4f} = ${trade_value:.2f}")
        logger.info(f"   Time: {current_time}")
        logger.info(f"   Type: {order_type}")
        
        return True
    
    def confirm_trade_exit(self, pair: str, trade, order_type: str, amount: float, 
                          rate: float, time_in_force: str, exit_reason: str, 
                          current_time, **kwargs) -> bool:
        """
        Exit confirmation with profit tracking
        """
        trade_value = amount * rate
        profit_pct = trade.calc_profit_ratio(rate) * 100
        profit_usd = trade.calc_profit(rate)
        
        logger.info(f"🚪 EXIT CONFIRMED: {pair}")
        logger.info(f"   Amount: {amount:.4f} @ ${rate:.4f} = ${trade_value:.2f}")
        logger.info(f"   Profit: {profit_pct:.2f}% (${profit_usd:.2f})")
        logger.info(f"   Reason: {exit_reason}")
        logger.info(f"   Duration: {current_time - trade.open_date}")
        
        return True
    
    def leverage(self, pair: str, current_time, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: str, 
                side: str, **kwargs) -> float:
        """
        No leverage - spot trading only
        """
        return 1.0
