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

    def __init__(self, config, exchange: Exchange, cache: Cache, base_asset: str):
        self.cache = cache
        self.seconds_to_update_cache = config['periodMax']['secondsToUpdateCache']
        self.base_asset = base_asset

        self.exchange = exchange
        self.period_used_in_days = config['periodMax']['periodUsedInDays']
        self.cache_key_name = f'max-value-in-{self.period_used_in_days}-days'

        if config['periodMax']['cacheUpdater']['enabled']:
            threading.Thread(target=self.__cache_updater).start()

    def should_place_order(self, df, current_price: float, symbol: str) -> bool:
        max_price = self.cache.hget(self.cache_key_name, symbol)
        if max_price == None:
            return False
        return current_price > float(max_price)

    def __cache_updater(self):
        logging.info('Start running PeriodMax cache updater')
        symbols_period_max = {}

        try:
            symbols_period_max = self.__build_symbols_period_max()
        except Exception as e:
            logging.error(f'Fail to update cache, error={e}')

        while True:
            try:
                self.cache.hset(self.cache_key_name, symbols_period_max)
                logging.info('PeriodMax cache updated successfully')
                time.sleep(self.seconds_to_update_cache)
                symbols_period_max = self.__build_symbols_period_max()
            except Exception as e:
                logging.error(f'Fail to update cache, error={e}')
                time.sleep(self.seconds_to_update_cache)

    def __build_symbols_period_max(self):
        threads = []
        symbols_period_max = {}

        def update_max_for_symbol(symbol):
            klines = self.exchange.get_klines(
                symbol, '1d', self.period_used_in_days)
            HIGH_POSITION = 2
            max_for_symbol = max(
                list(map(lambda x: float(x[HIGH_POSITION]), klines)))
            symbols_period_max[symbol] = max_for_symbol  # must be thread-safe.

        current_prices = self.exchange.get_current_prices()
        for current_price in current_prices:
            symbol = current_price['symbol']
            if not symbol.endswith(self.base_asset):
                continue
            threads.append(threading.Thread(
                target=update_max_for_symbol, kwargs={'symbol': symbol}))

        # binance client start discarding connections for higher numbers.
        MAX_SIMULTANEOUS_THREADS = 8

        for i, t in enumerate(threads):
            t.start()
            if (i+1) % MAX_SIMULTANEOUS_THREADS == 0:
                for j in range(MAX_SIMULTANEOUS_THREADS):
                    threads[i-j].join()

        for t in threads:
            t.join()

        return symbols_period_max
