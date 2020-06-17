import getopt
import math
import sys
import datetime
from typing import List
import time
import numpy as np
import shift


def hftTrader(available_bp):
    tradeType = np.random.randint(0, 2)
    intervalmean = available_bp / 2
    intervalsd = available_bp / 20
    tradeSize = int(np.random.normal(intervalmean, intervalsd))
    return (tradeType, tradeSize)

def main():
    my_username = "test001"
    my_password = "password"
    trader = shift.Trader(my_username)

    # connect
    try:
        trader.connect("initiator.cfg", my_password)
    except shift.IncorrectPasswordError as e:
        print(e)
        sys.exit(2)
    except shift.ConnectionTimeoutError as e:
        print(e)
        sys.exit(2)

    # subscribe to all available order books
    trader.sub_all_order_book()

    time.sleep(30)
    hftTimeDelta = np.random.lognormal(60, 20)
    currHFTTradeTime = trader.get_last_trade_time()
    nextHFTTradeTime = currHFTTradeTime + datetime.timedelta(seconds=hftTimeDelta)
    available_bp = 1000000
    orders = []

    while True:
        if currHFTTradeTime >= nextHFTTradeTime:
            print(currHFTTradeTime)
            hftTradeVals = hftTrader(available_bp)
            stock = trader.get_stock_list()[np.random.randint(0, 30)]
            print(stock)
            if hftTradeVals[0] == 0:
                x = trader.get_best_price(stock).get_ask_price()
                print(x)
                print(hftTradeVals[1])
                submittedOrder = shift.Order(shift.Order.Type.MARKET_BUY, stock, int(hftTradeVals[1] // (x * 100)))
                trader.submit_order(submittedOrder)
                orders.append(submittedOrder.id)
            else:
                x = trader.get_best_price(stock).get_bid_price()
                print(x)
                print(hftTradeVals[1])
                submittedOrder = shift.Order(shift.Order.Type.MARKET_SELL, stock, int(hftTradeVals[1] // (x * 100)))
                trader.submit_order(submittedOrder)
                orders.append(submittedOrder.id)
            hftTimeDelta = np.random.lognormal(60, 20)
            currHFTTradeTime = trader.get_last_trade_time()
            nextHFTTradeTime = currHFTTradeTime + datetime.timedelta(seconds=hftTimeDelta)
            available_bp = available_bp - trader.get_portfolio_item(stock).get_long_price()
            print(available_bp)
            print(nextHFTTradeTime)

            while available_bp <= 10000:
                index = np.random.randint(0, len(orders))
                # make more efficient to delete
                orderClose = orders[index]
                if trader.get_order(orderClose).type == shift.Order.Type.MARKET_BUY:
                    ticker = trader.get_order(orderClose).symbol
                    size = trader.get_order(orderClose).size
                    submittedOrder = shift.Order(shift.Order.Type.MARKET_SELL, ticker, size)

                else:
                    ticker = trader.get_order(orderClose).symbol
                    size = trader.get_order(orderClose).size
                    submittedOrder = shift.Order(shift.Order.Type.MARKET_BUY, ticker, size)
                trader.submit_order(submittedOrder)
                available_bp = available_bp + trader.get_order(submittedOrder.id).executed_price * size
                del orders[index]


if __name__ == "__main__":
    main()
