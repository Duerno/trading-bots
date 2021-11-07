def get_time_unit_in_full(interval: str) -> str:
    unit_in_full = {
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks',
    }

    if interval[-1] not in unit_in_full:
        raise ValueError(f'invalid unit: "{interval[-1]}"')

    return unit_in_full[interval[-1]]


def interval_to_seconds(interval: str) -> int:
    seconds_per_unit = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
        'w': 60 * 60 * 24 * 7,
    }

    if len(interval) < 2 or interval[-1] not in seconds_per_unit:
        raise ValueError(f'invalid interval: "{interval}"')

    return int(interval[:-1]) * seconds_per_unit[interval[-1]]
