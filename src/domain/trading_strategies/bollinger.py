import logging

from . import TradingStrategy


class Bollinger(TradingStrategy):
    """
    Bollinger is a trading strategy that uses Bollinger Bands to decide when to
    enter a trade.

    When does it send a green signal to enter a trade?
        When the current price is below the lower Bollinger Band technical
        indicator and the current delta between the upper and lower Bollinger
        Bands is greater than a pre-defined minimum.
    """

    def __init__(self, config):
        # min_relative_bands_delta represents the minimum acceptable percentage
        # of the typical price the delta between the upper and lower Bollinger
        # Bands should be so that we can place an order.
        self.min_relative_bands_delta = float(
            config['bollinger']['minRelativeBandsDelta'])

    def should_place_order(self, df, current_price: float, symbol: str) -> bool:
        bollinger_up = df.iloc[-1]['bollinger_up']
        bollinger_low = df.iloc[-1]['bollinger_low']
        bollinger_delta = bollinger_up - bollinger_low
        min_bollinger_delta = self.min_relative_bands_delta * df.iloc[-1]['tp']

        logging.info('Bollinger strategy params computed ' +
                     f'price={current_price} ' +
                     f'bbup={bollinger_up} ' +
                     f'bblow={bollinger_low} ' +
                     f'bbdelta={bollinger_delta} ' +
                     f'min_bbdelta={min_bollinger_delta}')

        return current_price < bollinger_low and bollinger_delta > min_bollinger_delta
