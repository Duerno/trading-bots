from typing import List, Dict

import click
import logging
import time
from matplotlib import pyplot as plt

from src.domain.entities import trading_states
from src.domain.exchanges import Exchange, fake, utils
from src.domain.trading_strategies import TradingStrategy, bollinger, dma
from src.gateways.binance import binance
from src.gateways.backtest import backtest


@click.command()
@click.option('--exchange-name', help='Define the exchange to be used. (options: binance|backtest|fake)')
@click.option('--trading-strategies', help='Define the trading strategies to be used, separated by comma. (options: bollinger|dma)')
@click.pass_context
def serial_trader(ctx, exchange_name, trading_strategies):
    """
    Serial Trader is a simple bot for trading serially using multiple trading
    strategies.

    Given a pair of assets and the chosen trading strategies, the Serial Trader
    bot enters and exits trades serially, i.e. creating only one trade at a
    time.

    Bot workflow:

        It has only two trading states (Pending and Trading) and the bot keeps
        indefinitely alternating between them.

        * The Pending state means that there aren't any ongoing trades. When
          that's the case, the bot gets the historical data for the chosen
          asset and tries to enter a trade by checking all available trading
          strategies.

        * The Trading state means that there is an ongoing trade. When that's
          the case, the bot only waits until the trade finishes.
    """
    config = ctx.obj['config']

    asset_to_trade = config['serialTrader']['assetToTrade']
    base_asset = config['serialTrader']['baseAsset']

    # initialize exchange.
    exchange: Exchange = None
    if exchange_name == 'binance':
        exchange = binance.Binance(config, base_asset)
    elif exchange_name == 'backtest':
        exchange = backtest.Backtest(config, base_asset, asset_to_trade)
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
    if len(strategies) == 0:
        raise ValueError('No valid strategy found in: %s' % trading_strategies)

    # initialize and run bot.
    bot = SerialTrader(config, exchange, strategies)
    bot.run()


class SerialTrader:
    def __init__(self, config: Dict, exchange: Exchange, strategies: List[TradingStrategy]):
        self.exchange = exchange
        self.strategies = strategies

        botConfig = config['serialTrader']
        self.cycle_time_in_seconds = botConfig['cycleTimeInSeconds']
        self.asset_to_trade = botConfig['assetToTrade']
        self.base_asset = botConfig['baseAsset']
        self.plot_results = botConfig['plotResults']
        self.stop_loss_percentage = float(botConfig['stopLossPercentage'])
        self.stop_gain_percentage = float(botConfig['stopGainPercentage'])
        self.base_asset_usage_percentage = float(
            botConfig['baseAssetUsagePercentage'])

    def run(self):
        logging.info('Start running Serial Trader bot')
        while True:
            try:
                self.__run_internal()
            except Exception as e:
                logging.error(f'Fail to run Serial Trader error={e}')
                self.exchange.reset_client()
            time.sleep(self.cycle_time_in_seconds)

    def __run_internal(self):
        logging.debug('Running Serial Trader trading verification')

        state = self.exchange.get_trading_state(self.asset_to_trade)

        if state == trading_states.PENDING:
            klines = self.exchange.get_historical_klines(self.asset_to_trade)
            df = self.__enrich_klines_with_indicators(klines)
            price = self.exchange.get_current_price(self.asset_to_trade)

            should_place_order = False
            for strategy in self.strategies:
                should_place_order = strategy.should_place_order(
                    df, price, utils.build_symbol(self.asset_to_trade, self.base_asset))
                if should_place_order:
                    break

            if should_place_order:
                base_asset_balance = self.exchange.get_base_asset_balance()
                base_asset_amount = base_asset_balance * self.base_asset_usage_percentage / 100
                buy_order, sell_order = self.exchange.place_order(
                    self.asset_to_trade,
                    base_asset_amount,
                    self.stop_loss_percentage,
                    self.stop_gain_percentage)
                self.__report_placed_order(buy_order, sell_order, klines)

        elif state == trading_states.TRADING:
            logging.debug('Waiting order to complete')
            return

    def __enrich_klines_with_indicators(self, klines):
        klines['tp'] = (klines['close'] + klines['low'] + klines['high']) / 3
        klines['std'] = klines['tp'].rolling(20).std(ddof=0)
        klines['sma_20'] = klines['tp'].rolling(20).mean()
        klines['sma_50'] = klines['tp'].rolling(50).mean()
        klines['sma_200'] = klines['tp'].rolling(200).mean()
        klines['bollinger_low'] = klines['sma_20'] - 2*klines['std']
        klines['bollinger_up'] = klines['sma_20'] + 2*klines['std']
        return klines

    def __report_placed_order(self, buy_order, sell_order, klines):
        if self.plot_results:
            # mplfinance.plot(klines[['open', 'high', 'low', 'close', 'volume']], type='candle', ax=ax)
            plt.plot(klines[['close', 'bollinger_low', 'bollinger_up']])
            plt.show()
