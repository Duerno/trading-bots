import binance as bnb

from src.domain.exchanges import utils


class HistoricalDataManager():

    def __init__(self, config):
        pass

    def get_historical_data(config, interval_in_minutes, base_asset, assets_to_trade):
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
                f'{interval_in_minutes}m',
                f'{interval_in_minutes * total_num_intervals} minutes ago UTC')

        return data
