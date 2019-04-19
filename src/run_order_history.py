from collections import defaultdict
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import datetime
import matplotlib.pyplot as plt


def run_order_history(order_list, ticks, data, output_path, chunks=20, starting_balance=1000, slippage=0.001, fees=0.00075):
    """Run a full simulation applying asset management against the simulated orders.

    Args:
        order_list: The orders logged during the simulation.
        ticks: All of the ticks iterated over during the simulation.
        data: The symbol data from the simulation.
        output_path: The location to store the results.
        chunks: How many pieces to split our total assets into.
        starting_balance: The starting balance to use for this operation.
        slippage: How much slippage to apply to orders, 0.001 for 1%.
        fees: How much to remove for fees, 0.001% for 1%.
    """

    fees = 1 - fees
    slippage_down = 1 - slippage
    slippage_up = 1 + slippage

    # Get the historical data used in the test and reformat for efficient use.
    stacked_sequence = {}
    prices = {}
    for tick in ticks:
        stacked_sequence[tick] = []
        prices[tick] = {}

    for symbol, points in data.items():
        for i in range(len(points["close"])):
            close = points["close"][i]
            time = points["time"][i]
            prices[time][symbol] = close


    for symbol, orders in order_list.items():
        for order in orders:
            time = order["time"]
            stacked_sequence[time].append(order)

    tick_times = list(ticks)
    tick_times = sorted(tick_times)


    balance = starting_balance
    value_points = []
    active_positions = {}

    # Store whatever the last price we saw was, accounts for gaps in prices.
    live_price = defaultdict(float)

    # Iterate through the test timespan and operate the account.
    for tick in tick_times:
        p = prices[tick]

        for symbol,  v in p.items():
            live_price[symbol] = v
        orders = stacked_sequence[tick]

        for order in orders:
            if order["type"] == "buy":
                if len(active_positions) < chunks:
                    # How much can we allocate, account for fees and slippage?
                    chunk_size = balance / (chunks - len(active_positions))
                    balance -= chunk_size
                    tokens = (chunk_size * fees) / (order["price"] * slippage_up)
                    active_positions[order["symbol"]] = tokens
                else:
                    # We've allocated all of our funds at this point.
                    pass
            else:
                if order["symbol"] not in active_positions:
                    continue
                # Make the sale and account for fees and slippage.
                tokens = active_positions[order["symbol"]]
                del active_positions[order["symbol"]]
                return_chunk = (tokens * (order["price"] * slippage_down) * fees)
                balance += return_chunk

        # Calculate the current total value.
        total_value = balance
        for key, value in active_positions.items():
            try:
                total_value += live_price[key] * value
            except:
                print ("There might be an issue with the data.")
        value_points.append(total_value)

    # Format the date data for charting.
    translated_dates = []
    for k in tick_times:
        t = datetime.datetime.utcfromtimestamp(int(k) / 1000)
        translated_dates.append(t)
    plt.plot(translated_dates, value_points)

    # Plot an output chart.
    plt.xlabel('time')
    plt.ylabel('portfolio value')
    plt.title('% Increase')
    plt.grid(True)
    plt.savefig("{}.png".format(output_path))
    plt.clf()
