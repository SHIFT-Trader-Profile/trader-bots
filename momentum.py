"""
MOMENTUM TRADING STRATEGY
7/12/2020 6:20pm

WHAT NEEDS TO BE ADDED:
--------------------------------------------
Place orders
Stop-loss strategy
Keep in mind we will need to pass the outputs of the algorithm into
the trading strategy. Take this into account when designing.
--------------------------------------------

IDEA FOR STORING OUTPUTS OF ALGORITHM:
--------------------------------------------
Maybe use a dictionary that could hold all the outputs of the algorithm.

data = {
    "AAPL": {
        "gain_threshold": 0.40,
        "loss_threshold": 0.30,
        "emergency_threshold": 0.0,
        "sma_interval": 0,
        "lma_interval": 0,
    }
}
--------------------------------------------
"""

import shift
import datetime
import time

def update_moving_averages(trader, moving_averages, stock):
    prices = trader.get_sample_prices(stock)
    moving_averages[stock][0] = round(sum(prices[-10:]) / 10, 2)
    moving_averages[stock][1] = round(sum(prices) / 60, 2)

    return

def get_initial_data(trader, moving_averages):
    for stock in trader.get_stock_list():
        # [small moving average, large moving average]
        moving_averages[stock] = [0, 0]
        trader.request_sample_prices(stock, 60, 60)

    time.sleep(3600)

    for stock in trader.get_stock_list():
        update_moving_averages(trader, moving_averages, stock)

    return

def momentum_strategy(trader, moving_averages):
    get_initial_data(trader, moving_averages)

    while True:
        time.sleep(60)
        for stock in trader.get_stock_list():
            prev_sma = moving_averages[stock][0]
            prev_lma = moving_averages[stock][1]
            update_moving_averages(trader, moving_averages, stock)

            if prev_sma < prev_lma and \
               moving_averages[stock][0] > moving_averages[stock][1]:
                # buying opportunity
            elif prev_sma > prev_lma and \
                 moving_averages[stock][0] < moving_averages[stock][1]:
                # selling opportunity

def main():
    trader = shift.Trader("test001")

    try:
        trader.connect("initiator.cfg", "password")
        trader.sub_all_order_book()
        if trader.get_last_trade_time().year == 1969:
            pass
    except shift.IncorrectPasswordError as e:
        print(e)
    except shift.ConnectionTimeoutError as e:
        print(e)

    momentum_strategy(trader, {})

    trader.disconnect()

    return

if __name__ == "__main__":
    main()
