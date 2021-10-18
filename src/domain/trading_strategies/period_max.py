import logging

from . import TradingStrategy


class PeriodMax(TradingStrategy):
    """
    PeriodMax is a trading strategy that compares the current value with the
    maximum value of a given period to decide when to enter a trade.

    When does it send a green signal to enter a trade?
        When the current value is higher than the maximum value of a given
        period, the trend is up and the strategy would say to buy.
    """

    def __init__(self, config):
        pass

    def should_place_order(self, df, current_price):
        # TODO
        return False
