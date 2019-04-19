from abc import ABC, abstractmethod
from collections import defaultdict

import json
import os
import pandas as pd


class AlphaPrototype(ABC):
    """Abstract base class that does the heavy lifting for a strategy class.

    Attributes:
        symbol_data: A dictionary of OHLCV keyed on the symbol.
        orders: A dictionary keyed by timestamp, which contains a list of orders.
        starting_balance: The starting balance for the simulation.
        balance: The balance, updated during the simulation.
        tokens: The number of tokens currently held, updated during the simulation.
        holding: A flag that states whether at this timestep, we are holding tokens.
        last_price: The last price for the symbol trading with.
        current_ticks: The ticks used in the current symbol data set.
        all_ticks: All of the ticks uesd across all subsets of the simulation."""

    def __init__(self, data_source, starting_balance, data_root="Data/", whitelist=None, exclusions=None):
        """Instantiates a model test.

        Args:
            data_source: Which data folder to import from.
            starting_balance: What balance the simulation should start with.
            data_root: Which sub-folder of data to operate on.
            whitelist: An optional list of symbols to use.
            exclusions: An optional list of symbols to ignore.
        """
        self.data_source = data_source
        self.data_root = data_root

        self.whitelist = whitelist
        self.exclusions = () if exclusions is None else exclusions

        self.symbol_data = {}
        self.load_data()
        self.orders = defaultdict(list)
        self.starting_balance = starting_balance
        self.balance = starting_balance
        self.tokens = 0
        self.holding = False
        self.last_price = -1
        self.current_ticks = set()
        self.all_ticks = set()

    def load_data(self):
        """Loads test data, ignoring excluded files, or importing only whitelisted data."""
        mypath = self.data_root + self.data_source
        onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        if self.whitelist is None:
            self.whitelist = set([f.split("_")[0] for f in onlyfiles])

        required_data = [f for f in onlyfiles
                         if f.split("_")[0] in self.whitelist
                         and f.split("_") not in self.exclusions]

        for file in required_data:
            symbol = file.split("_")[0]
            file_path = "{}/{}".format(mypath, file)

            with open(file_path) as f:
                print ("loading", file_path)
                file_contents = json.load(f)
                time = []
                open_values = []
                high = []
                low = []
                close = []
                volume = []
                for row in file_contents:
                    time.append(float(row[0]))
                    open_values.append(float(row[1]))
                    high.append(float(row[2]))
                    low.append(float(row[3]))
                    close.append(float(row[4]))
                    volume.append(float(row[5]))

            self.symbol_data[symbol] = pd.DataFrame.from_dict({
                "time": time,
                "open": open_values,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            })

    @abstractmethod
    def pre_backtest_calculations(self, value):
        """Abstract method for carrying out pre-backtest calculations."""
        return

    @abstractmethod
    def step(self, symbol, data, i):
        """Example function with PEP 484 type annotations.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            The return value. True for success, False otherwise.

        """
        return

    def buy(self, symbol, price, time):
        """Make a buy order for the simulation.

        Args:
            symbol: The symbol.
            price: The price of the symbol when buying.
            time: The time of the purchase.

        Returns:
            Whether the purchase was successful. True for success, False otherwise.
        """

        if self.holding:
            return False

        # Apply 1% slippage.
        purchase_price = price * 1.01

        # Apply fees.
        fees = 1 - 0.001
        self.balance *= fees

        # Calculate cost.
        self.tokens = self.balance / purchase_price
        self.balance = 0
        self.holding = True
        self.last_price = purchase_price
        self.orders[symbol].append({"symbol": symbol, "type": "buy", "price": price, "time": time})

        return True

    def sell(self, symbol, price, time):
        """Make a sell order for the simulation.

        Args:
            symbol: The symbol.
            price: The price of the symbol when selling.
            time: The time of the sale.

        Returns:
            Whether the sale was successful. True for success, False otherwise.
        """
        if not self.holding:
            return False

        # Apply 1% slippage.
        sale_price = price * 0.99

        fees = 1 - 0.001
        self.balance = self.tokens * sale_price
        self.balance *= fees

        self.tokens = 0
        self.holding = False
        self.last_price = -1
        self.orders[symbol].append({"symbol": symbol, "type": "sell", "price": price, "time": time})

        return True

    def run_backtest(self):
        """Iterates all test data, calculates and invokes results methods."""
        for key, value in self.symbol_data.items():
            self.balance = self.starting_balance
            self.tokens = 0
            self.holding = False
            self.last_price = -1
            self.current_ticks = set()

            self.pre_backtest_calculations(value)
            data_length = len(value["close"].values)

            for i in range(data_length):
                self.current_ticks.add(value["time"].values[i])
                self.step(key, value, i)

            # Add the value of the tokens on at the end, if there are any.
            token_value = self.tokens * value["close"].values[-1]
            self.balance += token_value
            self.all_ticks = self.all_ticks.union(self.current_ticks)
            self.print_results(key)
        self.print_full_results()

    @abstractmethod
    def print_results(self, symbol):
        """Abstract method for printing results for individual symbols.

        Args:
            symbol: The symbol currently traded on.
        """
        print (symbol)
        print ("profit:", self.balance - self.starting_balance)

    @abstractmethod
    def print_full_results(self):
        """Abstract method for outputting custom results."""
        return