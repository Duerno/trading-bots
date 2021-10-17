from typing import List, Dict

import click
import logging
import time
from matplotlib import pyplot as plt

from ..domain.entities import trading_states
from ..domain.exchanges import Exchange, fake
from ..domain.trading_strategies import TradingStrategy, bollinger, dma
from ..gateways.binance import binance, simulator


@click.command()
@click.option('--exchange-name', help='Define the exchange to be used. (options: binance|binance-simulator|fake)')
@click.option('--trading-strategies', help='Define the trading strategies to be used, separated by comma. (options: bollinger|dma)')
@click.pass_context
def one_time_opportunity_finder(ctx, exchange_name, trading_strategies):
    """
    TODO

    Bot workflow:

        TODO
    """
    config = ctx.obj['config']

    exchange = binance.Binance(config, "ADA", "USDT")

    logging.info(f'PRICE: {exchange.get_current_price()}')

    logging.info(f'PRODUCTS: {exchange.binance_client.get_products()}')
