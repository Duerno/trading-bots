import logging
from typing import Dict

from src.gateways.backtest.historical_data_manager import HistoricalDataManager
from src.domain.entities import trading_states
from src.domain.exchanges import Exchange, utils


class Backtest(Exchange):
    def __init__(self, config, base_asset, assets_to_trade=None):
        self.order = None
        self.balance = 1.0
        self.losses = 0
        self.gains = 0

        self.base_asset = base_asset
        self.tax = float(config['backtest']['taxPerTransaction'])

        self.frame_size = int(config['backtest']['frameSize'])
        self.current_data_index = self.frame_size - 1  # first index.
        self.historical_data = HistoricalDataManager.get_historical_data(config, base_asset, assets_to_trade)

    def get_market_depth(self, asset_to_trade: str):
        return None  # not supported yet.

    def get_trading_state(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        data = self.historical_data[symbol]

        self.current_data_index += 1

        # Ignore last trade when the simulation ends.
        if self.current_data_index >= len(data):
            return trading_states.PENDING

        if not self.order:
            return trading_states.PENDING

        current_price = self.get_current_price(asset_to_trade)
        buy_price = self.order['price']
        gain_price = self.order['gain_price']
        loss_price = self.order['loss_price']

        if current_price > gain_price:
            self.gains += 1
            multiplier = gain_price / buy_price - self.tax / 100.0
            self.balance += self.order['quantity'] * multiplier
            logging.warning(f'Sell finished with gain order={self.order}')
            self.order = None
            return trading_states.PENDING

        if current_price < loss_price:
            self.losses += 1
            multiplier = loss_price / buy_price - self.tax / 100.0
            self.balance += self.order['quantity'] * multiplier
            logging.warning(f'Sell finished with loss order={self.order}')
            self.order = None
            return trading_states.PENDING

        return trading_states.TRADING

    def get_ongoing_trades(self):
        return []

    def get_base_asset_balance(self):
        return self.balance

    def place_order(self, asset_to_trade: str, base_asset_usage_percentage, stop_loss_percentage, stop_gain_percentage):
        logging.debug(f'Placing order data_index={self.current_data_index}')

        price = self.get_current_price(asset_to_trade)
        gain_price = price * (100 + stop_gain_percentage + 2*self.tax) / 100.0
        loss_price = price * (100 - stop_loss_percentage + 2*self.tax) / 100.0
        quantity = self.balance * \
            (base_asset_usage_percentage / 100.0) * (1.0 - self.tax / 100.0)

        self.order = {
            'quantity': quantity,
            'price': price,
            'gain_price': gain_price,
            'loss_price': loss_price,
        }
        self.balance -= self.balance * base_asset_usage_percentage / 100.0

        return None, None  # buy-order, sell-order

    def get_current_price(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        data = self.historical_data[symbol]
        return float(data.iloc[self.current_data_index]['close'])

    def get_current_prices(self):
        prices = []
        for symbol in self.historical_data:
            prices.append({
                'symbol': symbol,
                'price': float(self.historical_data[symbol].iloc[self.current_data_index]['close'])
            })
        return prices

    def get_historical_klines(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        data = self.historical_data[symbol]

        if self.current_data_index >= len(data):
            logging.warning('End of simulation ' +
                            f'losses={self.losses} ' +
                            f'gains={self.gains} ' +
                            f'balance={self.balance}')
            exit(1)

        begin = self.current_data_index - self.frame_size + 1
        end = self.current_data_index
        return data.iloc[begin:end].copy()

    def get_klines(self, symbol: str, interval: str, limit: int = 1) -> Dict:
        return {}

    def reset_client(self):
        pass
