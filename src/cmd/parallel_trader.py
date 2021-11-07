from typing import List, Dict

import click
import logging
import time
import traceback

from src.domain.utils import datetime
from src.domain.cache import Cache
from src.domain.exchanges import Exchange
from src.domain.trading_strategies import TradingStrategy, period_max
from src.gateways.redis import redis
from src.gateways.binance import binance


@click.command()
@click.option('--exchange-name', help='Define the exchange to be used. (options: binance)')
@click.option('--trading-strategies', help='Define the trading strategies to be used, separated by comma. (options: period-max)')
@click.pass_context
def parallel_trader(ctx, exchange_name, trading_strategies):
    """
    Parallel Trader is a bot for trading multiple asset pairs at the same time,
    always using the same base asset. It uses multiple trading strategies to
    identify gain opportunities.

    Given a base asset and the chosen trading strategies, the Parallel Trader
    bot checks for opportunities on any available asset pair considering the
    given base asset. If an opportunity is found and the user has enough
    resources, this bot starts a trade. It's important to notice that this bot
    only starts one trade at a time for each asset pair.

    Bot workflow:

        TODO
    """
    config = ctx.obj['config']

    base_asset = config['parallelTrader']['baseAsset']
    candle_size = config['parallelTrader']['candleSize']

    # initialize exchange.
    exchange: Exchange = None
    if exchange_name == 'binance':
        exchange = binance.Binance(config, base_asset)
    else:
        raise ValueError('invalid exchange name: %s' % exchange_name)

    # initialize cache.
    cache: Cache = redis.Redis(config)

    # initialize strategies.
    strategies: List[TradingStrategy] = []
    trading_strategies_list = str(trading_strategies).split(',')
    if 'period-max' in trading_strategies_list:
        strategies.append(period_max.PeriodMax(config, exchange, cache, base_asset, candle_size))
    if len(strategies) == 0:
        raise ValueError('no valid strategy found in: %s' % trading_strategies)

    # initialize and run bot.
    bot = ParallelTrader(config, exchange, strategies)
    bot.run()


class ParallelTrader:
    def __init__(self, config: Dict, exchange: Exchange, strategies: List[TradingStrategy]):
        self.exchange = exchange
        self.strategies = strategies

        botConfig = config['parallelTrader']
        self.cycle_time_in_seconds = datetime.interval_to_seconds(botConfig['cycleTime'])
        self.base_asset = botConfig['baseAsset']
        self.stop_loss_percentage = float(botConfig['stopLossPercentage'])
        self.stop_gain_percentage = float(botConfig['stopGainPercentage'])
        self.base_asset_amount_per_trade = float(
            botConfig['baseAssetAmountPerTrade'])

    def run(self):
        logging.info('Start running Parallel Trader bot')
        while True:
            try:
                self.__run_internal()
            except Exception as e:
                logging.error(
                    f'Fail to run Parallel Trader error={e} {traceback.format_exc()}')
                self.exchange.reset_client()
            time.sleep(self.cycle_time_in_seconds)

    def __run_internal(self):
        logging.debug('Running Parallel Trader trading verification')

        balance = self.exchange.get_base_asset_balance()
        if balance < self.base_asset_amount_per_trade:
            logging.debug(
                f'Skipping trading verification: insufficient {self.base_asset} balance')
            return

        ongoing_trades = self.exchange.get_ongoing_trades()
        logging.debug(f'Ongoing trades: {ongoing_trades}')

        current_prices = self.exchange.get_current_prices()
        for current_price in current_prices:
            symbol = current_price['symbol']
            price = float(current_price['price'])

            if not symbol.endswith(self.base_asset):
                continue

            if symbol in ongoing_trades:
                continue

            should_place_order = False
            for strategy in self.strategies:
                should_place_order = strategy.should_place_order(
                    None, price, symbol)
                if should_place_order:
                    break

            if should_place_order:
                logging.debug(
                    f'Placing order for symbol {symbol} (current price: {price})')
                self.exchange.place_order(
                    symbol.replace(self.base_asset, ''),
                    self.base_asset_amount_per_trade,
                    self.stop_loss_percentage,
                    self.stop_gain_percentage)
                balance -= self.base_asset_amount_per_trade

            if balance < self.base_asset_amount_per_trade:
                logging.debug(
                    f'Skipping verification for next currencies: insufficient {self.base_asset} balance')
                return
