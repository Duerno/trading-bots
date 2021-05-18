from typing import Dict


class TradingStrategy():
    """
    Trading strategies define when it is time to start a trade or not. The time
    to start a trade is mainly associated with the belief in the probable
    short-term appreciation of an asset, which creates a gain opportunity.

    To evaluate when we believe it worth entering a trade, trading strategies
    may define scenarios and conditions based on the recent historical data of
    an asset and it's current price, however, it may be as complex as doing a
    sentimental analysis based on social networks recent sharings or creating a
    deep neural network to identify patterns.
    """

    def __init__(self, config: Dict):
        pass

    def should_place_order(self, df, current_price: float) -> bool:
        pass
