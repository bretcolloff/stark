# S.T.A.R.K (Simple Trading Algorithm Research Kit)

**STARK** is a tool developed to simplify the process of discovering plausible models for trading cryptocurrencies. The importers and such are Binance specific, as it's currently the most reliable cryptocurrency exchange for algorithm trading.

**Disclaimer**: Use the software provided here at your own risk.

## Setup
To get started I've provided 2 ways to manage your dependencies. If you're using Python > 3.5, you can simply install the requirements through pip if you're happy to install the dependencies into your default environment:
> pip install -r requirements.txt

However, if you would rather use a virtual environment, a Pipenv and Pipenv.lock file have been provided. The environment can be created and started with:
> pipenv install
> pipenv shell

This should allow you to run the python scripts now with the correct dependencies.

## Getting Started
Running the `build_data_directory.py` script will create a `Data/Test` folder and populate it with a large window of ETHBTC data at 1 hour candles. The existing models should now run and generate output charts.

## Building New Models
To build a new model, create a new directory under `models`, and create your model class in there. As demonstrated in the examples, you need to implement the `AlphaPrototype` base class, and some of the abstract methods.

The two most important are `step` and `pre_backtest_calculations`.

### Implementing `step`
The step method requires 3 parameters in addition to self, which are `symbol, data, i`.
> **symbol**: Is simply the market symbol, used to access the OHLCV data that was loaded during instantiation.
**data**: Is the dictionary that contains all of the OHLCV for all of the data loaded for the test, be careful not to use data that has not been seen yet during the test when making decisions or predicting.
**i**: Is the current index of the OHLCV data in the simulation for this specific symbol. As different currencies are added at different points in time, the data starts at different points for each currency.

The two key actions to will carry out are `self.buy` and `self.sell`, which both take the same parameters:
> **symbol**: The symbol of the asset being purchased. This is because directories with multiple symbol data files store order actions in the same place, so that an 'all up' simulation of asset management can be carried out later, it's actually closer to just storing which signals we can use.
> **price**: The price of the asset at the time of purchase, but this will change at the point of storage because we simulate deductions due to fees and variations caused by slippage.
> **time**: The close time of the candle that the order is made at.

The base class has the `holding` attribute that will tell you if some of the tokens are already being held during this simulation.

### Implementing `pre_backtest_calculations`
This method is the place to calculate indicators that you plan to use during your model execution. In some of the example models you can see that some moving averages, RSI, ADX, etc. are calculated and then used in the `step` method.

It takes a single parameter, `value`, which is a Pandas DataFrame with the test data for this symbol, under the columns `open, high, low, close, volume, time`. The library `finta` which is in the dependencies to run the examples contains a large array of indicators that can be calculated simply by passing in `value`, though additional parameters such as `period` can be used to state the period of a moving average, or other specifics that can be found in the `finta` documentation [here](https://github.com/peerchemist/finta).


