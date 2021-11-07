import time
import logging
import threading
import math

from src.domain.cache import Cache
from src.domain.exchanges import Exchange, utils
from src.domain.utils import datetime

from . import TradingStrategy


class PeriodMax(TradingStrategy):
    """
    PeriodMax is a trading strategy that compares the current value with the
    maximum value of a given period to decide when to enter a trade.

    When does it send a green signal to enter a trade?
        When the current value is higher than the maximum value of a given
        period, the trend is up and the strategy would say to buy.
    """

    def __init__(self, config, exchange: Exchange, cache: Cache, base_asset: str, interval: str):
        self.cache = cache
        self.seconds_to_update_cache = config['periodMax']['secondsToUpdateCache']
        self.base_asset = base_asset

        # Validate period to be used.
        num_intervals = int(config['periodMax']['numIntervals'])
        interval_in_seconds = num_intervals * datetime.interval_to_seconds(interval)
        one_day_in_seconds = datetime.interval_to_seconds('1d')
        if interval_in_seconds % one_day_in_seconds != 0:
            raise ValueError(f'Invalid period: "{num_intervals} * {interval}" should be multiple of "1d"')

        self.exchange = exchange
        self.num_days = interval_in_seconds / one_day_in_seconds
        self.cache_key_name = f'max-value-in-{self.num_days}-days'

        if str(config['periodMax']['cacheUpdater']['enabled']).lower() == 'true':
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
            asset_to_trade = symbol.replace(self.base_asset, '')
            klines = self.exchange.get_historical_klines(asset_to_trade, '1d', self.num_days)
            max_for_symbol = max(list(map(lambda x: float(x[utils.HIGH_INDEX]), klines)))
            symbols_period_max[symbol] = max_for_symbol  # must be thread-safe.

        current_prices = self.exchange.get_current_prices()
        for current_price in current_prices:
            symbol = current_price['symbol']
            if not symbol.endswith(self.base_asset):
                continue
            threads.append(threading.Thread(target=update_max_for_symbol, kwargs={'symbol': symbol}))

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
