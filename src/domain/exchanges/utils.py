import numpy
import pandas


def parse_klines(raw_klines):
    klines = pandas.DataFrame(raw_klines, columns='''
            open_time
            open
            high
            low
            close
            volume
            close_time
            quote_volume
            number_of_trades
            taker_buy_base_volume
            taker_buy_quote_volume
            can_be_ignored
        '''.split(), dtype=numpy.float64)

    klines['time'] = pandas.to_datetime(
        klines['open_time'].apply(lambda x: int(x)),
        unit='ms')
    klines = klines.set_index('time')

    return klines


def fix_asset_precision(asset, precision: int = 5):
    fixed_asset = ''
    digit_count = 0
    dot_found = False
    for char in str(asset):
        if char == '.':
            dot_found = True
            if dot_found and digit_count >= precision:
                break
            fixed_asset += char
        else:
            if digit_count >= precision:
                if dot_found:
                    break
                fixed_asset += '0'
            else:
                fixed_asset += char
            digit_count += 1
    return fixed_asset


def build_symbol(asset_to_trade: str, base_asset: str):
    return '{}{}'.format(asset_to_trade, base_asset)
