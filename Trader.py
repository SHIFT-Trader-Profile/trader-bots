from abc import ABC, abstractmethod
import time
import shift
import numpy as np
import datetime
import sys
from math import exp

# Trader ----------------------------------------------------------------------

class Trader(ABC):
    def __init__(self, username: str, password: str, verbose: bool):
        self._verbose = verbose
        self._trader = shift.Trader(username)
        self._orders = []
        self._next_trade_time = None
        self._available_bp = 0
        self._risk_tolerance = 0

        if self._verbose:
            self.__username = username

        try:
            print(f"Attempting to connect as {username}...")
            self._trader.connect("initiator.cfg", password)
            self._trader.sub_all_order_book()
        except shift.IncorrectPasswordError as e:
            print(e)
            sys.exit(1)
        except shift.ConnectionTimeoutError as e:
            print(e)
            sys.exit(1)

    def _get_trade_size(self, stock: str, typ: shift.Order.Type):
        if typ == shift.Order.Type.MARKET_BUY:
            best_price = self._trader.get_best_price(stock).get_ask_price()
        else:
            best_price = self._trader.get_best_price(stock).get_bid_price()

        mean = np.log(self._available_bp / 2)
        sd = np.log(self._available_bp / 100)
        cost = exp(np.random.normal(mean, sd))

        if self._verbose:
            print(f"Mean: {mean}\nSD: {sd}\nCost: {cost}")

        self._available_bp -= cost

        return int(cost / best_price / 100)

    def _get_next_trade_time(self, lower: int, upper: int, minutes: bool):
        while self._trader.get_last_trade_time().year == 1969:
            pass

        n = np.random.randint(lower, upper)
        delta = datetime.timedelta(minutes=n) if minutes else datetime.timedelta(seconds=n)
        self._next_trade_time = self._trader.get_last_trade_time() + delta

        if self._verbose:
            print(f"{self.__username}'s next trade time is: {self._next_trade_time}")


    def can_trade(self):
        return self._trader.get_last_trade_time() >= self._next_trade_time


    def execute_trade(self):
        stock = self._trader.get_stock_list()[np.random.randint(0, 30)]

        if np.random.binomial(n=1, p=0.5) == 0:
            typ = shift.Order.Type.MARKET_BUY
        else:
            typ = shift.Order.Type.MARKET_SELL

        order = shift.Order(typ, stock, self._get_trade_size(stock, typ))
        self._orders.append(order)
        self._trader.submit_order(order)
        time.sleep(1)

        if self._verbose:
            print(f"BP: {self._trader.get_portfolio_summary().get_total_bp()}")

# Small Trader ----------------------------------------------------------------

class SmallTrader(Trader):
    __bounds = (10, 420) # Lower and upper bound for _next_trade_time Minutes

    def __init__(self, username: str, password: str, verbose: bool):
        Trader.__init__(self, username, password, verbose)
        self._available_bp = np.random.randint(10000, 200000)
        self._get_next_trade_time(*SmallTrader.__bounds, True)

    def execute_trade(self):
        Trader.execute_trade(self)
        self._get_next_trade_time(*SmallTrader.__bounds, True)

# High-Frequency Trader -------------------------------------------------------

class HighFrequencyTrader(Trader):
    __bounds = (0, 300) # Lower and upper bound for _next_trade_time. Seconds

    def __init__(self, username: str, password: str, verbose: bool):
        Trader.__init__(self, username, password, verbose)
        self._available_bp = 1000000
        self._get_next_trade_time(*HighFrequencyTrader.__bounds, False)

    def execute_trade(self):
        Trader.execute_trade(self)
        self._get_next_trade_time(*HighFrequencyTrader.__bounds, False)

# Market-Maker ----------------------------------------------------------------

