from typing import List, Dict

import click
import logging
import time
from matplotlib import pyplot as plt

from ..domain.entities import trading_states
from ..domain.exchanges import Exchange, fake
from ..domain.trading_strategies import TradingStrategy, bollinger, dma, period_max
from ..gateways.binance import binance, simulator


@click.command()
@click.option('--exchange-name', help='Define the exchange to be used. (options: binance|binance-simulator|fake)')
@click.option('--trading-strategies', help='Define the trading strategies to be used, separated by comma. (options: bollinger|dma|period_max)')
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

    # initialize exchange.
    exchange: Exchange = None
    if exchange_name == 'binance':
        exchange = binance.Binance(config, base_asset)
    elif exchange_name == 'binance-simulator':
        exchange = simulator.BinanceSimulator(config, base_asset)
    elif exchange_name == 'fake':
        exchange = fake.FakeExchange(config, base_asset)
    else:
        raise ValueError('Invalid exchange name: %s' % exchange_name)

    # initialize strategies.
    strategies: List[TradingStrategy] = []
    trading_strategies_list = str(trading_strategies).split(',')
    if 'bollinger' in trading_strategies_list:
        strategies.append(bollinger.Bollinger(config))
    if 'dma' in trading_strategies_list:
        strategies.append(dma.DualMovingAverage(config))
    if 'period_max' in trading_strategies_list:
        strategies.append(period_max.PeriodMax(config))
    if len(strategies) == 0:
        raise ValueError('No valid strategy found in: %s' % trading_strategies)

    # initialize and run bot.
    bot = ParallelTrader(config, exchange, strategies)
    bot.run()


class ParallelTrader:
    def __init__(self, config: Dict, exchange: Exchange, strategies: List[TradingStrategy]):
        self.exchange = exchange
        self.strategies = strategies

        botConfig = config['parallelTrader']
        self.cycle_time_in_seconds = botConfig['cycleTimeInSeconds']
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
                logging.error(f'Fail to run Parallel Trader error={e}')
                self.exchange.reset_client()
            time.sleep(self.cycle_time_in_seconds)

    def __run_internal(self):
        logging.debug('Running Parallel Trader trading verification')

        base_asset_balance = self.get_base_asset_balance()
        if base_asset_balance < self.base_asset_amount_per_trade:
            return

        # should return a list of asset names.
        ongoing_trades = self.exchange.get_assets_in_trade()

        # should return map of asset_name to price if asset_name is not passed as argument.
        current_prices = self.get_current_price()

        for asset_name, price in current_prices:
            if asset_name in ongoing_trades:
                continue

            should_place_order = False
            for strategy in self.strategies:
                should_place_order = strategy.should_place_order(df, price)
                if should_place_order:
                    break

            if should_place_order:
                buy_order, sell_order = self.exchange.place_order(
                    asset_name,
                    self.base_asset_usage_percentage,
                    self.stop_loss_percentage,
                    self.stop_gain_percentage)
                self.__report_placed_order(buy_order, sell_order, klines)
