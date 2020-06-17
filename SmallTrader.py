import getopt
import math
import sys
import datetime
from typing import List
import time
import numpy as np
import shift



def smallTrader(available_bp):
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


    print("started")
    time.sleep(30)
    smallTradeExecuteTime = np.random.randint(0, 450)
    currSmallTradeTime = trader.get_last_trade_time()
    print(currSmallTradeTime)
    nextSmallTradeTime = currSmallTradeTime + datetime.timedelta(seconds=3)
    available_bp = np.random.randint(10000, 200000)
    print(available_bp)
    print(nextSmallTradeTime)
    orders = []

    while True:
        time.sleep(1)
        currSmallTradeTime = trader.get_last_trade_time()
        print(currSmallTradeTime)
        if currSmallTradeTime >= nextSmallTradeTime:
            print(currSmallTradeTime)
            smallTradeVals = smallTrader(available_bp)
            stock = trader.get_stock_list()[np.random.randint(0, 30)]
            print(stock)
            if smallTradeVals[0] == 0:
                x = trader.get_best_price(stock).get_ask_price()
                print(x)
                print(smallTradeVals[1])
                submittedOrder = shift.Order(shift.Order.Type.MARKET_BUY, stock, int(smallTradeVals[1] // (x * 100)))
                trader.submit_order(submittedOrder)
                orders.append(submittedOrder.id)
            else:
                x = trader.get_best_price(stock).get_bid_price()
                print(x)
                print(smallTradeVals[1])
                submittedOrder = shift.Order(shift.Order.Type.MARKET_SELL, stock, int(smallTradeVals[1] // (x * 100)))
                trader.submit_order(submittedOrder)
                orders.append(submittedOrder.id)
            smallTradeExecuteTime = np.random.randint(0, 450)
            currSmallTradeTime = trader.get_last_trade_time()
            nextSmallTradeTime = currSmallTradeTime + datetime.timedelta(minutes=smallTradeExecuteTime)
            available_bp = available_bp - trader.get_portfolio_item(stock).get_long_price()
            print(available_bp)
            print(nextSmallTradeTime)

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
