import time
import logging
import threading

from src.domain.cache import Cache
from src.domain.exchanges import Exchange

from . import TradingStrategy


class PeriodMax(TradingStrategy):
    """
    PeriodMax is a trading strategy that compares the current value with the
    maximum value of a given period to decide when to enter a trade.

    When does it send a green signal to enter a trade?
        When the current value is higher than the maximum value of a given
        period, the trend is up and the strategy would say to buy.
    """

    def __init__(self, config, exchange: Exchange, cache: Cache):
        self.cache = cache
        self.seconds_to_update_cache = config['periodMax']['secondsToUpdateCache']

        self.exchange = exchange
        self.period_used = config['periodMax']['periodUsed']
        self.cache_key_name = f'max-value-in-{self.period_used}'

        if config['periodMax']['cacheUpdater']['enabled']:
            threading.Thread(target=self.__cache_updater).start()

    def should_place_order(self, df, current_price: float, symbol: str) -> bool:
        max_price_str = self.cache.hget(self.cache_key_name, symbol)
        if max_price_str == None:
            return False
        return current_price > float(max_price_str)

    def __cache_updater(self):
        logging.info('Start running PeriodMax cache updater')
        while True:
            try:
                # TODO(duerno): implement this.
                pass
            except Exception as e:
                logging.error(f'Fail to update cache, error={e}')
            time.sleep(self.seconds_to_update_cache)
