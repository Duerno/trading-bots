from typing import Dict


class Exchange:
    """
    Exchange is an interface that defines the implementation of all wrappers
    that communicates to any real-world or simulated stock or cryptocurrency
    exchange.
    """

    def __init__(self, config: Dict, symbol: str):
        pass

    def get_market_depth(self):
        pass

    def get_trading_state(self):
        pass

    def get_base_asset_balance(self):
        pass

    def place_order(self, **kwargs):
        pass

    def get_current_price(self):
        pass

    def get_historical_klines(self, **kwargs):
        pass

    def reset_client(self):
        pass
