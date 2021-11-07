import binance as bnb

from src.domain.exchanges import utils
from src.domain.utils import datetime


class HistoricalDataManager():

    def __init__(self, config):
        pass

    def get_historical_data(config: dict, interval: str, base_asset: str, assets_to_trade: str) -> dict:
        binance_api_key = config['binance']['api']['key']
        binance_api_secret = config['binance']['api']['secret']
        binance_client = bnb.Client(binance_api_key, binance_api_secret)

        total_num_intervals = int(config['backtest']['totalNumberOfIntervals'])

        if assets_to_trade == None:
            assets_to_trade = list()
            tickers = binance_client.get_all_tickers()
            for ticker in tickers:
                symbol = ticker['symbol']
                if not symbol.endswith(base_asset):
                    continue
                assets_to_trade.append(symbol)

        data = dict()
        for asset in assets_to_trade:
            symbol = utils.build_symbol(asset, base_asset)

            # TODO: cache data instead of requesting from Binance everytime.
            data[symbol] = binance_client.get_historical_klines(
                symbol,
                interval,
                f'{total_num_intervals} {datetime.get_time_unit_in_full(interval)} ago UTC')

        return data
