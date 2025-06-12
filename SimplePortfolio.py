from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class SimplePortfolio(IStrategy):
    INTERFACE_VERSION = 3
    
    # More flexible settings for accumulation
    minimal_roi = {"0": 0.25}  # 25% target (hold longer)
    stoploss = -0.25           # 25% stop loss (more room)
    timeframe = '2h'           # Less frequent checks
    process_only_new_candles = True
    startup_candle_count = 20
    can_short = False
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Simple RSI only
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # VERY AGGRESSIVE accumulation - buy almost always
        dataframe.loc[
            (dataframe['rsi'] < 65),  # Buy when RSI under 65 (very relaxed)
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Almost never sell (let ROI handle exits)
        dataframe.loc[
            (dataframe['rsi'] > 90),  # Only sell when extremely overbought
            'exit_long'] = 1
        
        return dataframe
