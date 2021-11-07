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

        # since we observed Binance API returning lower data then asked, we
        # are adding a little extra time the the total time used.
        EXTRA_TIME = 200

        total_num_intervals = int(config['backtest']['totalNumberOfIntervals'])
        total_time = total_num_intervals * int(interval[:-1]) + EXTRA_TIME

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
            data_for_symbol = binance_client.get_historical_klines(
                symbol,
                interval,
                f'{total_time} {datetime.get_time_unit_in_full(interval)} ago UTC')

            data[symbol] = list(data_for_symbol[:total_num_intervals])
            if len(data[symbol]) != total_num_intervals:
                raise ValueError(f'Data fetch error: {len(data[symbol])} should be equal to {total_num_intervals}')

        return data
