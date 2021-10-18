import time
import logging
import binance as bnb

from ...domain.entities import trading_states
from ...domain.exchanges import Exchange, utils


class Binance(Exchange):
    def __init__(self, config, base_asset):
        self.tax_per_transaction = float(
            config['binance']['taxPerTransaction'])
        self.interval_in_minutes = int(
            config['binanceSimulator']['intervalInMinutes'])

        self.api_key = config['binance']['api']['key']
        self.api_secret = config['binance']['api']['secret']
        self.binance_client = bnb.Client(self.api_key, self.api_secret)
        self.base_asset = base_asset

    def get_market_depth(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        return self.binance_client.get_order_book(symbol=symbol)

    def get_trading_state(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        orders = self.binance_client.get_open_orders(symbol=symbol)
        if len(orders) == 0:
            return trading_states.PENDING
        else:
            return trading_states.TRADING

    def get_base_asset_balance(self):
        return self.binance_client.get_asset_balance(asset=self.base_asset)

    def place_order(self, asset_to_trade: str, base_asset_usage_percentage, stop_loss_percentage, stop_gain_percentage):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        base_asset_balance = self.get_base_asset_balance()

        quantity_base_asset = float(
            base_asset_balance['free']) * base_asset_usage_percentage / 100

        logging.debug('Buy order params ' +
                      f'quantity_base_asset={quantity_base_asset} ' +
                      f'base_asset_balance={base_asset_balance}')

        buy_order = self.binance_client.order_market_buy(
            symbol=symbol,
            quoteOrderQty=utils.fix_asset_precision(quantity_base_asset, precision=4))
        logging.info('Buy order (market) executed successfully ' +
                     f'quantity_base_asset={quantity_base_asset} ' +
                     f'base_asset_balance={base_asset_balance} ' +
                     f'buy_order={buy_order}')

        price_asset_to_trade = float(buy_order['fills'][0]['price'])
        gain_price = price_asset_to_trade * \
            (100 + stop_gain_percentage + 2*self.tax_per_transaction) / 100.0
        loss_price = price_asset_to_trade * \
            (100 - stop_loss_percentage + 2*self.tax_per_transaction) / 100.0

        quantity_asset_to_trade = float(
            buy_order['executedQty']) * (99.999 - self.tax_per_transaction) / 100.0

        # wait 1s to guarantee correct history order in Binance UI.
        time.sleep(1)

        logging.debug('Sell order params ' +
                      f'quantity_asset_to_trade={quantity_asset_to_trade} ' +
                      f'price_asset_to_trade={price_asset_to_trade} ' +
                      f'loss_price={loss_price} ' +
                      f'gain_price={gain_price}')

        sell_order = self.binance_client.create_oco_order(
            symbol=symbol,
            side=bnb.Client.SIDE_SELL,
            quantity=utils.fix_asset_precision(
                quantity_asset_to_trade, precision=4),
            price=utils.fix_asset_precision(gain_price),
            stopPrice=utils.fix_asset_precision(loss_price),
            stopLimitPrice=utils.fix_asset_precision(loss_price),
            stopLimitTimeInForce=bnb.Client.TIME_IN_FORCE_GTC)
        logging.info('Sell order (OCO) placed successfully ' +
                     f'quantity_asset_to_trade={quantity_asset_to_trade} ' +
                     f'price_asset_to_trade={price_asset_to_trade} ' +
                     f'loss_price={loss_price} ' +
                     f'gain_price={gain_price} ' +
                     f'sell_order={sell_order}')

        return buy_order, sell_order

    def get_current_price(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        res = self.binance_client.get_all_tickers(symbol)
        return float(res['price'])

    def get_historical_klines(self, asset_to_trade: str, num_intervals=210):
        self.reset_client()  # avoid connection problems.
        raw_klines = self.binance_client.get_historical_klines(
            utils.build_symbol(asset_to_trade, self.base_asset),
            f'{self.interval_in_minutes}m',
            f'{self.interval_in_minutes * num_intervals} minutes ago UTC')
        return utils.parse_klines(raw_klines)

    def reset_client(self):
        self.binance_client = bnb.Client(self.api_key, self.api_secret)
