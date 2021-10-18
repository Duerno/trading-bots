import logging

from . import binance
from ...domain.entities import trading_states
from ...domain.exchanges import Exchange, utils


class BinanceSimulator(Exchange):
    def __init__(self, config, base_asset, asset_to_trade='ADA'):
        self.order = None
        self.balance = 1.0
        self.losses = 0
        self.gains = 0

        binance_exchange = binance.Binance(config, base_asset)
        self.tax = binance_exchange.tax_per_transaction

        self.base_asset = base_asset
        self.asset_to_trade = asset_to_trade

        interval_in_minutes = int(
            config['binanceSimulator']['intervalInMinutes'])
        num_intervals = int(config['binanceSimulator']['numberOfIntervals'])

        raw_klines = binance_exchange.binance_client.get_historical_klines(
            utils.build_symbol(asset_to_trade, base_asset),
            f'{interval_in_minutes}m',
            f'{interval_in_minutes * num_intervals} minutes ago UTC')
        self.historical_data = utils.parse_klines(raw_klines)
        self.frame_size = 210
        self.current_data_index = self.frame_size - 1

    def get_market_depth(self, asset_to_trade: str):
        return None

    def get_trading_state(self, asset_to_trade: str):
        self.current_data_index += 1

        if not self.order:
            return trading_states.PENDING

        current_price = self.get_current_price()
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

        price = self.get_current_price()
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
        return float(self.historical_data.iloc[self.current_data_index]['close'])

    def get_current_prices(self):
        return [
            {
                "symbol": utils.build_symbol(self.asset_to_trade, self.base_asset),
                "price": "40000.02"
            }
        ]

    def get_historical_klines(self, asset_to_trade: str):
        if self.current_data_index >= len(self.historical_data):
            logging.warning('End of simulation ' +
                            f'losses={self.losses} ' +
                            f'gains={self.gains} ' +
                            f'balance={self.balance}')
            exit(1)

        begin = self.current_data_index - self.frame_size + 1
        end = self.current_data_index
        return self.historical_data.iloc[begin:end].copy()

    def reset_client(self):
        pass
