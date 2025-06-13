from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import logging

logger = logging.getLogger(__name__)

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # Weekly accumulation settings
    minimal_roi = {"0": 0.30}  # 30% profit target (hold longer)
    stoploss = -0.12           # 12% stop loss
    timeframe = '1h'           
    process_only_new_candles = True
    startup_candle_count = 30
    can_short = False
    
    # Position management for weekly cycles
    position_adjustment_enable = True
    max_entry_position_adjustment = 4  # Up to 4 additional buys per week
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Indicators optimized for weekly accumulation
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_slow'] = ta.RSI(dataframe, timeperiod=21)
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        
        # MACD for trend confirmation
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        
        # Volume analysis
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        
        # Bollinger Bands for oversold conditions
        bb = ta.BBANDS(dataframe)
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_upper'] = bb['upperband']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Aggressive weekly accumulation - buy on multiple conditions
        dataframe.loc[
            (
                # Primary conditions (any one triggers buy)
                (dataframe['rsi'] < 70) |  # Not extremely overbought
                (dataframe['close'] < dataframe['bb_middle']) |  # Below BB middle
                (dataframe['close'] < dataframe['ema_26']) |  # Below longer EMA
                (dataframe['macd'] < dataframe['macd_signal'])  # MACD bearish
            ) &
            # Safety conditions (all must be true)
            (dataframe['rsi'] > 20) &  # Not extremely oversold
            (dataframe['volume'] > dataframe['volume_sma'] * 0.3) &  # Some volume
            (dataframe['close'] > dataframe['sma_50'] * 0.85),  # Not in severe downtrend
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Very conservative exit - focus on accumulation
        dataframe.loc[
            (dataframe['rsi'] > 85) &  # Extremely overbought
            (dataframe['close'] > dataframe['bb_upper']) &  # Above upper BB
            (dataframe['macd'] > dataframe['macd_signal']) &  # MACD bullish
            (dataframe['close'] > dataframe['ema_12'] * 1.15),  # 15% above short EMA
            'exit_long'] = 1
        
        return dataframe
    
    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, 
                            min_stake, max_stake, **kwargs):
        """
        Dollar cost averaging - add more when price drops
        Designed for weekly refill cycle
        """
        # Get day of week (0=Monday, 6=Sunday)
        current_day = current_time.weekday()
        
        # More aggressive adding early in the week (Monday-Wednesday)
        if current_day <= 2:  # Monday to Wednesday
            profit_threshold = -0.03  # Add when down 3%
        else:  # Thursday to Sunday
            profit_threshold = -0.06  # Add when down 6%
        
        if current_profit < profit_threshold:
            try:
                # Calculate additional stake (smaller amounts for more frequent adding)
                if current_profit < -0.10:  # Down 10%+
                    additional_stake = min_stake * 1.2  # 120% of minimum
                elif current_profit < -0.05:  # Down 5-10%
                    additional_stake = min_stake * 1.0  # 100% of minimum
                else:  # Down 3-5%
                    additional_stake = min_stake * 0.8  # 80% of minimum
                
                logger.info(f"📈 Adding to {trade.pair}: profit={current_profit:.2%}, "
                          f"additional=${additional_stake:.2f}, day={current_day}")
                return additional_stake
                
            except Exception as e:
                logger.error(f"❌ Position adjustment error: {e}")
        
        return None
    
    def custom_stake_amount(self, pair: str, current_time, current_rate: float,
                          proposed_stake: float, min_stake: float, max_stake: float,
                          entry_tag: str, **kwargs) -> float:
        """
        Dynamic stake sizing for weekly cycles
        """
        # Get day of week
        current_day = current_time.weekday()
        
        # Larger positions early in week when balance is fresh
        if current_day <= 1:  # Monday-Tuesday (refill day)
            stake_multiplier = 1.3
        elif current_day <= 3:  # Wednesday-Thursday
            stake_multiplier = 1.1
        else:  # Friday-Sunday (preserve some funds)
            stake_multiplier = 0.9
        
        # Calculate final stake amount
        final_stake = max(
            proposed_stake * stake_multiplier,
            min_stake * 1.1  # Always 10% above minimum
        )
        
        # Don't exceed max stake
        final_stake = min(final_stake, max_stake)
        
        logger.info(f"💰 Stake for {pair}: ${final_stake:.2f} (day {current_day}, "
                   f"multiplier {stake_multiplier})")
        
        return final_stake
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                          time_in_force: str, current_time, entry_tag, **kwargs) -> bool:
        """
        Final check before entering trade
        """
        # Log the trade for monitoring
        logger.info(f"🎯 Entering {pair}: {amount:.4f} @ ${rate:.4f} = ${amount * rate:.2f}")
        return True
