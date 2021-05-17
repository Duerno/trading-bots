import click
import logging
import time
from matplotlib import pyplot as plt
from ..gateways.binance import binance, fake_binance
from ..domain.entities import trading_states


@click.command()
@click.pass_context
def bollinger(ctx):
    """
    Bollinger is a trading bot that uses Bollinger Bands to decide when to
    enter a trade.
    """
    config = ctx.obj['config']

    asset_to_trade = config['bollinger']['assetToTrade']
    base_asset = config['bollinger']['baseAsset']
    exchange = binance.Binance(config, asset_to_trade, base_asset)
    # exchange = fake_binance.FakeBinance(config, asset_to_trade, base_asset)

    bot = Bollinger(config, exchange)
    bot.run()


class Bollinger:
    def __init__(self, config, exchange):
        self.plot_results = config['bollinger']['plotResults']
        self.base_asset_usage_percentage = float(
            config['bollinger']['baseAssetUsagePercentage'])
        self.stop_loss_percentage = float(
            config['bollinger']['stopLossPercentage'])
        self.stop_gain_percentage = float(
            config['bollinger']['stopGainPercentage'])
        self.exchange = exchange

    def run(self):
        logging.info('Start running bollinger bot')
        while True:
            try:
                self.__run_internal()
            except Exception as e:
                logging.error(f'Fail to run bollinger error={e}')
                self.exchange.reset_client()
            time.sleep(15)

    def __run_internal(self):
        logging.debug('Running bollinger trading verification')

        state = self.exchange.get_trading_state()

        if state == trading_states.PENDING:
            klines = self.exchange.get_historical_klines()
            df = self.enrich_klines_with_indicators(klines)
            current_price = self.exchange.get_current_price()
            if self.should_place_order(df, current_price):
                buy_order, sell_order = self.exchange.place_order(
                    self.base_asset_usage_percentage,
                    self.stop_loss_percentage,
                    self.stop_gain_percentage)
                self.report_placed_order(
                    buy_order,
                    sell_order,
                    klines)
        elif state == trading_states.TRADING:
            logging.info('Waiting order to complete')
            return

    def enrich_klines_with_indicators(self, klines):
        klines['tp'] = (klines['close'] + klines['low'] + klines['high']) / 3
        klines['std'] = klines['tp'].rolling(20).std(ddof=0)
        klines['sma'] = klines['tp'].rolling(20).mean()
        klines['bollinger_low'] = klines['sma'] - 2*klines['std']
        klines['bollinger_up'] = klines['sma'] + 2*klines['std']
        return klines

    def should_place_order(self, df, current_price):
        bollinger_up = df.iloc[-1]['bollinger_up']
        bollinger_low = df.iloc[-1]['bollinger_low']
        bollinger_delta = bollinger_up - bollinger_low
        volatility_threshold = 0.04 * df.iloc[-1]['tp']

        logging.info('Params of should_place_order computed ' +
                     f'price={current_price} ' +
                     f'bbup={bollinger_up} ' +
                     f'bblow={bollinger_low} ' +
                     f'bbdelta={bollinger_delta} ' +
                     f'v_th={volatility_threshold}')

        return current_price < bollinger_low and bollinger_delta > volatility_threshold

    def report_placed_order(self, buy_order, sell_order, klines):
        if self.plot_results:
            # mplfinance.plot(klines[['open', 'high', 'low', 'close', 'volume']], type='candle', ax=ax)
            plt.plot(klines[['close', 'bollinger_low', 'bollinger_up']])
            plt.show()
