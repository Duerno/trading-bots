import time
import logging
import binance as bnb
from typing import Dict, Union

from src.domain.exchanges import Exchange, utils
from src.domain.utils import datetime


class Binance(Exchange):
    """
    This is a wrapper for the Binance Exchange.

    Binance is the world's largest crypto exchange.
    Official website: http://binance.com
    Trade rules reference: https://www.binance.com/en/trade-rule
    List of API errors: https://github.com/binance/binance-spot-api-docs/blob/master/errors.md
    Tick size article: https://www.binance.com/en/support/announcement/9e1c939434c7453cae2e23ec6e43c283
    Symbol filters: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#filters
    """

    def __init__(self, config, base_asset):
        self.tax_per_transaction = float(config['binance']['taxPerTransaction'])

        self.api_key = config['binance']['api']['key']
        self.api_secret = config['binance']['api']['secret']
        self.binance_client = bnb.Client(self.api_key, self.api_secret)

        self.exchange_info = self.__get_exchange_info()
        self.base_asset = base_asset

    def get_market_depth(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        return self.binance_client.get_order_book(symbol=symbol)

    def get_ongoing_trades(self):
        return list(map(lambda order: order['symbol'], self.binance_client.get_open_orders()))

    def get_base_asset_balance(self):
        return float(self.binance_client.get_asset_balance(asset=self.base_asset)['free'])

    def place_order(self, asset_to_trade: str, base_asset_amount, stop_loss_percentage, stop_gain_percentage):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        base_asset_amount = utils.fix_asset_precision(base_asset_amount)

        err = self.__validate_order(symbol, base_asset_amount, stop_loss_percentage)
        if err is not None:
            logging.warn(f'Ignoring order request: {err}')
            return None, None

        logging.debug('Buy order params ' +
                      f'base_asset_amount={base_asset_amount} ' +
                      f'asset_to_trade={asset_to_trade}')

        try:
            buy_order = self.binance_client.order_market_buy(
                symbol=symbol,
                quoteOrderQty=base_asset_amount)
        except Exception as e:
            logging.warn(f'Ignoring order request: {e}')
            return None, None

        logging.info('Buy order (market) executed successfully ' +
                     f'base_asset_amount={base_asset_amount} ' +
                     f'buy_order={buy_order}')

        # wait 1s to guarantee correct execution order in the exchange.
        time.sleep(1)

        price = float(buy_order['fills'][0]['price'])
        gain_price = price * (100 + stop_gain_percentage + 2*self.tax_per_transaction) / 100.0
        loss_price = price * (100 - stop_loss_percentage + 2*self.tax_per_transaction) / 100.0
        quantity = float(buy_order['executedQty']) * (99.999 - self.tax_per_transaction) / 100.0
        quantity, gain_price, loss_price = self.__fix_order_params(symbol, quantity, gain_price, loss_price)

        logging.debug('Sell order params ' +
                      f'quantity={quantity} ' +
                      f'price={price} ' +
                      f'loss_price={loss_price} ' +
                      f'gain_price={gain_price} ' +
                      f'tick_size={self.__get_tick_size(symbol)} ' +
                      f'step_size={self.__get_step_size(symbol)}')

        sell_order = self.binance_client.create_oco_order(
            symbol=symbol,
            side=bnb.Client.SIDE_SELL,
            quantity=quantity,
            price=gain_price,
            stopPrice=loss_price,
            stopLimitPrice=loss_price,
            stopLimitTimeInForce=bnb.Client.TIME_IN_FORCE_GTC)

        logging.info('Sell order (OCO) placed successfully ' +
                     f'quantity={quantity} ' +
                     f'price={price} ' +
                     f'loss_price={loss_price} ' +
                     f'gain_price={gain_price} ' +
                     f'sell_order={sell_order}')

        return buy_order, sell_order

    def get_current_price(self, asset_to_trade: str):
        symbol = utils.build_symbol(asset_to_trade, self.base_asset)
        res = self.binance_client.get_all_tickers(symbol)
        return float(res['price'])

    def get_current_prices(self):
        return self.binance_client.get_all_tickers()

    def get_historical_klines(self, asset_to_trade: str, interval: str, num_intervals: int) -> list:
        # reference: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#enum-definitions
        valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']
        if interval not in valid_intervals:
            raise ValueError(f'invalid interval: "{interval}"')

        data = self.binance_client.get_historical_klines(
            utils.build_symbol(asset_to_trade, self.base_asset),
            interval,
            f'{num_intervals * int(interval[:-1])} {datetime.get_time_unit_in_full(interval)} ago UTC')

        data = list(data[:num_intervals])
        if len(data) != num_intervals:
            raise ValueError(f'data fetch error: {len(data)} should be equal to {num_intervals}')

        return data

    def reset_client(self):
        self.binance_client = bnb.Client(self.api_key, self.api_secret)

    def __get_exchange_info(self):
        info = self.binance_client.get_exchange_info()

        symbols_info = {}
        for symbol_info in info['symbols']:
            symbols_info[symbol_info['symbol']] = symbol_info
            filters = {}
            for filter in symbols_info[symbol_info['symbol']]['filters']:
                filters[filter['filterType']] = filter
            symbols_info[symbol_info['symbol']]['filters'] = filters

        info['symbols'] = symbols_info
        return info

    def __validate_order(self, symbol, quantity_in_base_asset, stop_loss_percentage):
        current_price = float(self.binance_client.get_all_tickers(symbol)['price'])

        step_size = self.__get_step_size(symbol)
        quantity_in_base_asset = float(quantity_in_base_asset)
        quantity = quantity_in_base_asset / current_price
        truncated_quantity = float(utils.fix_asset_precision(quantity - (quantity % step_size)))

        tick_size = self.__get_tick_size(symbol)
        loss_price = current_price * (100 - stop_loss_percentage + 2*self.tax_per_transaction) / 100.0
        truncated_loss_price = float(utils.fix_asset_precision(loss_price - (loss_price % tick_size)))

        estimated_quantity_in_stop_loss = truncated_quantity * truncated_loss_price
        min_notional = self.__get_min_notional(symbol)

        if estimated_quantity_in_stop_loss < min_notional:
            return 'quantity for stop loss is lower than min notional'

        return None

    def __fix_order_params(self, symbol, quantity, gain_price, loss_price):
        step_size = self.__get_step_size(symbol)
        quantity = float(quantity)
        quantity = utils.fix_asset_precision(quantity - (quantity % step_size))

        tick_size = self.__get_tick_size(symbol)
        gain_price = float(gain_price)
        gain_price = utils.fix_asset_precision(gain_price - (gain_price % tick_size))
        loss_price = float(loss_price)
        loss_price = utils.fix_asset_precision(loss_price - (loss_price % tick_size))

        return quantity, gain_price, loss_price

    def __get_step_size(self, symbol):
        return float(self.exchange_info['symbols'][symbol]['filters']['LOT_SIZE']['stepSize'])

    def __get_tick_size(self, symbol):
        return float(self.exchange_info['symbols'][symbol]['filters']['PRICE_FILTER']['tickSize'])

    def __get_min_notional(self, symbol):
        return float(self.exchange_info['symbols'][symbol]['filters']['MIN_NOTIONAL']['minNotional'])
