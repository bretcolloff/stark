from src.base.alphaprototype import AlphaPrototype
from src.run_order_history import run_order_history

import talib as ta
import numpy as np


class BBAND_ADX(AlphaPrototype):
    """A combination bollinger band, adx and rsi model.

    Buy signal:
        - Close price of a candle dips below the lower bband line.
        - ADX is higher than 25.
        - RSI is higher than 70.

    Sell signal:
        - The close price of the candle is higher than the upper bband line.
        - RSI is less than 30."""
    
    def print_full_results(self):
        run_order_history(self.orders, self.all_ticks, self.symbol_data, "rsi_adx")

    def print_results(self, symbol):
        print ("processed", symbol)

    def pre_backtest_calculations(self, value):
        self.ema = ta.EMA(np.array(value["close"]))
        high = np.array(value["high"])
        low = np.array(value["low"])
        close = np.array(value["close"])

        self.adx = ta.ADX(high, low, close)
        self.rsi = ta.RSI(close)
        self.upper_bband, self.middle_bband, self.lower_bband = ta.BBANDS(close)

    def step(self, symbol, data, i):
        if data["close"][i] < self.lower_bband[i] and self.adx[i] > 25 and self.rsi[i] > 70:
            self.buy(symbol, data["close"][i], data["time"][i])
        if data["close"][i] > self.upper_bband[i] and self.rsi[i] < 30:
            self.sell(symbol, data["close"][i], data["time"][i])


strat = BBAND_ADX("1HETHBTC", 100, data_root="../../Data/")
strat.run_backtest()
