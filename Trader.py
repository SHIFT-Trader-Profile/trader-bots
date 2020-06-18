from abc import ABC, abstractmethod
import shift
import numpy as np
import datetime
import sys

# Trader ----------------------------------------------------------------------

class Trader(ABC):
    def __init__(self, username: str, password: str, verbose: bool):
        self._verbose = verbose
        self._trader = shift.Trader(username)
        self._orders = []
        self._next_trade_time = None
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


    @abstractmethod
    def _get_trade_size(self, stock: str, typ: shift.Order.Type) -> int:
        pass


    def _get_next_trade_time(self, lower: int, upper: int):
        while self._trader.get_last_trade_time().year == 1969:
            pass

        minutes = np.random.randint(lower, upper)
        self._next_trade_time = self._trader.get_last_trade_time() + datetime.timedelta(minutes=minutes)

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

# Small Trader ----------------------------------------------------------------

class SmallTrader(Trader):
    __bounds = (1, 2) # Lower and upper bound for _next_trade_time


    def __init__(self, username: str, password: str, verbose: bool):
        Trader.__init__(self, username, password, verbose)
        self.__available_bp = np.random.randint(10000, 200000)
        self._get_next_trade_time(*SmallTrader.__bounds)


    def _get_trade_size(self, stock: str, typ: shift.Order.Type):
        if typ == shift.Order.Type.MARKET_BUY:
            best_price = self._trader.get_best_price(stock).get_ask_price()
        else:
            best_price = self._trader.get_best_price(stock).get_bid_price()

        print(best_price)
        mean = self.__available_bp / 2
        sd = self.__available_bp / 20
        cost = np.random.lognormal(mean, sd)
        print(cost)

        self.__available_bp -= cost

        return int(cost / best_price / 100)

# High-Frequency Trader -------------------------------------------------------

"""
class HighFrequencyTrader(Trader):
    __bounds = (0, 1) # Lower and upper bound for _next_trade_time


    def __init__(self, username: str, password: str, verbose: bool):
        Trader.__init__(self, username, password, verbose)
        self.__available_bp = 1000000
        self._get_next_trade_time(*HighFrequencyTrader.__bounds)


# Market-Maker ----------------------------------------------------------------

class MarketMaker(Trader):
    pass
"""