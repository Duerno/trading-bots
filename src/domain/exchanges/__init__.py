from typing import Dict
from pandas.core.frame import DataFrame


class Exchange:
    """
    Exchange is an interface that defines the implementation of all wrappers
    that communicates to any real-world or simulated stock or cryptocurrency
    exchange.
    """

    def __init__(self, config: Dict, base_asset: str):
        pass

    def get_market_depth(self, asset_to_trade: str):
        """
        Returns the order book for the asset pair (base_asset, asset_to_trade).
        """
        pass

    def get_trading_state(self, asset_to_trade: str):
        pass

    def get_ongoing_trades(self):
        pass

    def get_base_asset_balance(self) -> float:
        pass

    def place_order(self, asset_to_trade: str, **kwargs):
        pass

    def get_current_price(self, asset_to_trade: str):
        pass

    def get_current_prices(self):
        pass

    def get_historical_klines(self, asset_to_trade: str, **kwargs) -> DataFrame:
        pass

    def get_klines(self, symbol: str, interval: str, limit: int = 1) -> Dict:
        pass

    def reset_client(self):
        pass
