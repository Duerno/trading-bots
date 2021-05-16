from . import binance
from ...domain.entities import trading_states


class BinanceSimulator:
    def __init__(self, config, symbol):
        self.binance = binance.Binance(config, symbol)
        self.symbol = symbol
        self.order = None

    def get_market_depth(self):
        return self.binance.get_market_depth()

    def get_trading_state(self):
        # TODO(duerno): update order state
        if not self.order:
            return trading_states.PENDING
        else:
            return trading_states.TRADING

    def get_base_asset_balance(self):
        return self.binance.get_base_asset_balance()

    def place_order(self, base_asset_usage_percentage, stop_loss_percentage, stop_gain_percentage):
        # TODO(duerno): build simulated order
        return {}

    def get_current_price(self):
        return self.binance.get_current_price()

    def get_historical_klines(self, **kwargs):
        return self.binance.get_current_price(kwargs)
