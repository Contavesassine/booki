from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # Accumulation settings
    minimal_roi = {"0": 0.20}  # 20% profit target
    stoploss = -0.20           # 20% stop loss
    timeframe = '1h'           # Use supported 1h timeframe
    process_only_new_candles = True
    startup_candle_count = 20
    can_short = False
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Simple RSI for entry signals
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # AGGRESSIVE accumulation strategy - buy frequently
        dataframe.loc[
            (dataframe['rsi'] < 60),  # Buy when RSI under 60 (relaxed)
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Rarely sell - focus on accumulation
        dataframe.loc[
            (dataframe['rsi'] > 85),  # Only sell when very overbought
            'exit_long'] = 1
        
        return dataframe
