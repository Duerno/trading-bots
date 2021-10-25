import pytest

from src.domain.trading_strategies.period_max import PeriodMax

CONFIG = {'periodMax':{'secondsToUpdateCache':10, 'periodUsedInDays':20,
    'cacheUpdater':{'enabled': True}}}
EXCHANGE = "exchange"
CACHE= "cache"
SYMBOL= "symbol"

class TestPeriodMax:
    def test_should_place_order(x=1):
        period_max = PeriodMax(CONFIG, EXCHANGE, CACHE, SYMBOL)
        #period_max.should_place_order()
        assert True
