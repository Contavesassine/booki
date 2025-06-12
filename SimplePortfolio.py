from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # Simple settings
    minimal_roi = {"0": 0.20}  # 20% target (hold longer)
    stoploss = -0.20           # 20% stop loss
    timeframe = '4h'           # Check every 4 hours (less frequent)
    process_only_new_candles = True
    startup_candle_count = 30
    can_short = False
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Simple RSI for basic oversold detection
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Buy when RSI is oversold (simple DCA approach)
        dataframe.loc[
            (dataframe['rsi'] < 50),  # Buy when under 50 RSI (not too strict)
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Very rarely sell (let ROI handle exits)
        dataframe.loc[
            (dataframe['rsi'] > 85),  # Only sell when very overbought
            'exit_long'] = 1
        
        return dataframe
