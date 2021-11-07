from typing import Dict
from . import Exchange
from . import utils


class FakeExchange(Exchange):
    def __init__(self, config, base_asset):
        self.base_asset = base_asset
        pass

    def get_market_depth(self, asset_to_trade: str):
        return {
            'lastUpdateId': 4589770863,
            'bids': [
                ['47286.45000000', '0.00571200'],
                ['47286.29000000', '0.08220300']
            ],
            'asks': [
                ['47294.01000000', '0.94441200'],
                ['47294.02000000', '0.00143200']
            ]
        }

    def get_ongoing_trades(self):
        return []

    def get_base_asset_balance(self):
        # {
        #     'asset': 'USDT',
        #     'free': '136.76918981',
        #     'locked': '0.00000000'
        # }
        return 136.76918981

    def place_order(self, asset_to_trade: str, base_asset_amount, stop_loss_percentage, stop_gain_percentage):
        return {
            'symbol': 'ADAUSDT',
            'orderId': 1487106018,
            'orderListId': -1,
            'clientOrderId': 'nwpVB64GKBjwIkhmz3vYRI',
            'transactTime': 1621135401333,
            'price': '0.00000000',
            'origQty': '4.41000000',
            'executedQty': '4.41000000',
            'cummulativeQuoteQty': '10.00011600',
            'status': 'FILLED',
            'timeInForce': 'GTC',
            'type': 'MARKET',
            'side': 'BUY',
            'fills': [
                {
                    'price': '2.26760000',
                    'qty': '4.41000000',
                    'commission': '0.00441000',
                    'commissionAsset': 'ADA',
                    'tradeId': 160508167
                }
            ]
        }

    def get_current_price(self, asset_to_trade: str):
        return 47277.98

    def get_current_prices(self):
        return [
            {
                "symbol": utils.build_symbol("ADA", self.base_asset),
                "price": "47277.98"
            }
        ]

    def get_historical_klines(self, asset_to_trade: str, interval: str, num_intervals: int) -> list:
        return [
            [
                1621120500000,     # Open time
                '47677.72000000',  # Open
                '47781.79000000',  # High
                '47612.64000000',  # Low
                '47768.35000000',  # Close
                '18.42490400',     # Volume
                1621120559999,     # Close time
                '878556.8423303',  # Quote asset volume
                633,               # Number of trades
                '14.13153600',     # Taker buy base asset volume
                '673858.4037933',  # Taker buy quote asset volume
                '0'                # Can be ignored
            ], [
                1621120560000,
                '47768.52000000',
                '47848.76000000',
                '47726.03000000',
                '47734.10000000',
                '20.08872700',
                1621120619999,
                '960091.01225217',
                614,
                '13.85848500',
                '662385.50959035',
                '0'
            ], [
                1621120620000,
                '47727.49000000',
                '47762.15000000',
                '47623.00000000',
                '47670.98000000',
                '10.54932400',
                1621120679999,
                '502952.91539268',
                491,
                '5.09070500',
                '242721.43476742',
                '0'
            ]
        ]

    def reset_client(self):
        pass
