from src.base.alphaprototype import AlphaPrototype
from src.run_order_history import run_order_history

import talib as ta
import numpy as np


class RSI_ADX(AlphaPrototype):
    """An rsi and adx model.

    Buy signal:
        - RSI is less than the lower threshold.
        - RSI[-1] is greater than or equal to the lower threshold.
        - ADX is higher than the threshold.

    Sell signal:
        - RSI is higher than the upper threshold.
        - RSI[-1] is less than or equal to the upper threshold.
        - The close price is lower than the EMA."""

    def print_full_results(self):
        run_order_history(self.orders, self.all_ticks, self.symbol_data, "ema_rsi_adx", chunks=15)

    def print_results(self, symbol):
        print ("processed", symbol, "profit:", self.balance - self.starting_balance)

    def pre_backtest_calculations(self, value):
        self.ema = ta.EMA(np.array(value["close"]), timeperiod=self.ema_range)
        high = np.array(value["high"])
        low = np.array(value["low"])
        close = np.array(value["close"])

        self.adx = ta.ADX(high, low, close)
        self.rsi = ta.RSI(close)
        self.rsi_high = 90
        self.rsi_low = 30
        self.ema_range = 2

        self.adx_threshold = 25

    def step(self, symbol, data, i):
        if self.rsi[i] < self.rsi_low \
                and self.rsi[i-1] >= self.rsi_low \
                and self.adx[i] > self.adx_threshold:
            self.buy(symbol, data["close"][i], data["time"][i])
        elif \
                self.rsi[i] > self.rsi_high \
                and data["close"][i] < self.ema[i] \
                and self.rsi[i-1] <= self.rsi_high:
            self.sell(symbol, data["close"][i], data["time"][i])


strat = RSI_ADX("BTCONLY", 100, data_root="../../Data/")
strat.run_backtest()
