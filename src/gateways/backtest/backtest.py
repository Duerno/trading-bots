import logging

from src.gateways.backtest.historical_data_manager import HistoricalDataManager
from src.domain.exchanges import Exchange, utils


class Backtest(Exchange):
    def __init__(self, config: dict, interval: str, base_asset: str, assets_to_trade: str = None):
        self.ongoing_trades = {}
        self.balance = 1000.0
        self.losses = 0
        self.gains = 0

        self.base_asset = base_asset
        self.tax = float(config['backtest']['taxPerTransaction'])

        self.total_num_intervals = int(config['backtest']['totalNumberOfIntervals'])
        self.current_data_index = int(config['backtest']['startIntervalIndex'])
        self.historical_data = HistoricalDataManager.get_historical_data(
            config, interval, base_asset, assets_to_trade)

    def get_market_depth(self, asset_to_trade: str):
        return None  # not supported yet.

    def get_ongoing_trades(self):
        self.current_data_index += 1
        if self.current_data_index % 100 == 0:
            logging.info(f'Simulation step: {self.current_data_index}')

        # end backtest when the last frame is overpast.
        if self.current_data_index >= self.total_num_intervals:
            logging.info(f'End of simulation losses={self.losses} gains={self.gains} balance={self.balance}')
            exit(0)

        # end trades in stop gain/loss.
        for symbol in list(self.ongoing_trades):
            trade = self.ongoing_trades[symbol]

            buy_price = trade['price']
            gain_price = trade['gain_price']
            loss_price = trade['loss_price']
            quantity = trade['quantity']

            asset_to_trade = symbol.replace(self.base_asset, '')
            current_price = self.get_current_price(asset_to_trade)

            if current_price > gain_price:
                self.gains += 1
                multiplier = gain_price / buy_price - self.tax / 100.0
                self.balance += quantity * multiplier
                logging.info(f'Sell finished with gain={trade}')
                del self.ongoing_trades[symbol]

            if current_price < loss_price:
                self.losses += 1
                multiplier = loss_price / buy_price - self.tax / 100.0
                self.balance += quantity * multiplier
                logging.info(f'Sell finished with loss={trade}')
                del self.ongoing_trades[symbol]

        return list(self.ongoing_trades)

    def get_base_asset_balance(self):
        return self.balance

    def place_order(self, asset_to_trade: str, base_asset_amount, stop_loss_percentage, stop_gain_percentage):
        logging.debug(f'Placing order data_index={self.current_data_index}')

        price = self.get_current_price(asset_to_trade)
        gain_price = price * (100 + stop_gain_percentage + 2*self.tax) / 100.0
        loss_price = price * (100 - stop_loss_percentage + 2*self.tax) / 100.0
        quantity = base_asset_amount * (1.0 - self.tax / 100.0)

        # TODO: fix order params precision.
        # quantity, gain_price, loss_price = self.__fix_order_params(symbol, quantity, gain_price, loss_price)

        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        self.ongoing_trades[symbol] = {
            'quantity': quantity,
            'price': price,
            'gain_price': gain_price,
            'loss_price': loss_price,
        }
        self.balance -= base_asset_amount

        return None, None  # buy-order, sell-order

    def get_current_price(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        data = self.historical_data[symbol]
        return float(data[self.current_data_index][utils.CLOSE_INDEX])

    def get_current_prices(self):
        prices = []
        for symbol in self.historical_data:
            prices.append({
                'symbol': symbol,
                'price': float(self.historical_data[symbol][self.current_data_index][utils.CLOSE_INDEX])
            })
        return prices

    def get_historical_klines(self, asset_to_trade: str, interval: str, num_intervals: int) -> dict:
        if num_intervals > self.current_data_index + 1:
            raise ValueError(
                f'Failed to get klines: num_intervals ({num_intervals}) cannot be higher than current index ({self.current_data_index}) + 1')
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        data = self.historical_data[symbol]

        # TODO: use the provided interval instead of assuming it is equal to
        # the self.historical_data interval size.
        begin = self.current_data_index - num_intervals + 1
        end = self.current_data_index

        return data[begin:end]

    def reset_client(self):
        pass
