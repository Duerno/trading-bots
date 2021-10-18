import logging

from . import TradingStrategy


class DualMovingAverage(TradingStrategy):
    """
    DualMovingAverage (DMA) is a trading strategy that uses two Simple Moving
    Averages (SMA) to decide when to enter a trade, one shorter (that uses 50
    sample periods) and a larger (that uses 200 sample periods).

    When does it send a green signal to enter a trade?
        When the shorter moving average crosses above the larger moving
        average, the trend is up and the strategy would say to buy.
    """

    def __init__(self, config):
        pass

    def should_place_order(self, df, current_price: float, symbol: str) -> bool:
        sma_50 = df.iloc[-1]['sma_50']
        sma_200 = df.iloc[-1]['sma_200']

        logging.info('DMA strategy params computed ' +
                     f'price={current_price} ' +
                     f'sma_50={sma_50} ' +
                     f'sma_200={sma_200} ')

        return sma_50 > sma_200
