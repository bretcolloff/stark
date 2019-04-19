from binance.client import Client
from src.helpers.get_historical import get_historical_klines

import json


def get_symbol_history(path, symbol, interval=Client.KLINE_INTERVAL_1HOUR,
                  start="30 January, 2016", end="1 April, 2019"):
    """Populate a directory with data within a date range and interval for a symbol.

    Args:
        path: The directory in which to store the data.
        symbol: The symbol we want the data for.
        interval: The candle interval, eg. 1 hour, as a binance enum.
        start: The start date.
        end: The end date.
    """
    klines = get_historical_klines(symbol, interval, start, end)
    with open("{}/{}_1h.json".format(path, symbol), 'w') as f:
        f.write(json.dumps(klines))

def populate_data(path, base_currency="ETH", interval=Client.KLINE_INTERVAL_1HOUR,
                  start="30 January, 2016", end="1 April, 2019"):
    """Populate a directory for data within a time range and interval for a base asset.

    Args:
        path: The directory in which to store the data.
        base_currency: The base asset we want the data for.
        interval: The candle interval, eg. 1 hour, as a binance enum.
        start: The start date.
        end: The end date.
    """
    symbols = []

    client = Client("", "")
    tickers = client.get_all_tickers()
    for ticker in tickers:
        symbol = ticker['symbol']
        if symbol.endswith(base_currency):
            symbols.append(symbol)

    for symbol in symbols:
        klines = get_historical_klines(symbol, interval, start, end)
        with open("{}/{}_1h.json".format(path, symbol), 'w') as f:
            f.write(json.dumps(klines))
