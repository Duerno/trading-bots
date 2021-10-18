Trading Bots
============

This repository implements an ever evolving set of simple trading bots
developed to autonomously trade inside general or cryptocurrency Exchanges,
such as Binance.

## Getting Started

### Requirements

- Python ([installation](https://www.python.org/downloads/))
- Docker ([installation](https://docs.docker.com/get-docker/))

All other utilities are automatically downloaded in the configuration process.

### Run Locally

First, you have to setup your host. Just run the following command to install
the library dependencies:

```sh
pip3 install -r requirements.txt
```

Then, start the project dependencies by running the command below:

```sh
docker compose up redis -d
```

To check out the available bots and options, run the following command:

```sh
python3 main.py
```

One can customize the bots settings by either updating the
`config/default.yaml` file or defining environment variables. So that
variables can replace the config file settings, they must be all capitalized,
prefixed with `BOT_` and each different YAML hierarchy level must be separated
by an `_`.

As an example, one can setup some settings for the Binance Exchange and run the
`serial-trader` bot with some typical settings as following:

```sh
export BOT_BINANCE_API_KEY=my-super-secret-api-key
export BOT_BINANCE_API_SECRET=my-super-secret-api-secret
python3 main.py --log-level=info serial-trader --exchange-name=binance --trading-strategies=bollinger
```

Now, the chosen trading bot must be up and running. Enjoy!

### Test

Unfortunately, this project doesn't have any tests yet.

## Available Bots

Useful information about the available bots, how they work and their specific
settings.

For more information about the bots description, workflow and parameters
details, please run the CLI helper as following:

```sh
python3 main.py <BOT_NAME> --help
```

### Serial Trader

Serial Trader is a simple bot for trading serially using multiple trading
strategies.

Given a pair of assets and the chosen trading strategies, the Serial Trader
bot enters and exits trades serially, i.e. creating only one trade at a time.

### Parallel Trader

Parallel Trader is a bot for trading multiple asset pairs at the same time,
always using the same base asset. It uses multiple trading strategies to
identify gain opportunities.

Given a base asset and the chosen trading strategies, the Parallel Trader
bot checks for opportunities on any available asset pair considering the given
base asset. If an opportunity is found and the user has enough resources, this
bot starts a trade. It's important to notice that this bot only starts one
trade at a time for each asset pair.

## Available Trading Strategies

Useful information about the available trading strategies, how they work and
their specific settings.

### Bollinger

Bollinger is a trading strategy that uses Bollinger Bands to decide when to
enter a trade. Reference: [John Bollinger's Official Bollinger Band Website](https://www.bollingerbands.com).

### Dual Moving Averages

Dual Moving Average (DMA) is a trading strategy that uses two Simple Moving
Averages (SMA) to decide when to enter a trade. This two SMA have different
frame windows: one is shorter (uses 50 sample periods) and the other is larger
(uses 200 sample periods). Reference: [Moving Average Strategies](https://analyzingalpha.com/moving-average#moving-average-strategies).

### Period Max

PeriodMax is a trading strategy that compares the current value with the
maximum value of a given period to decide when to enter a trade.

## Available Exchanges

Useful information about the integrated exchanges, how they work and their
specific settings.

### Binance Cryptocurrency Exchange

[Binance Exchange](https://www.binance.com/) is a cryptocurrency exchange. The
current integration is powered by the [python-binance](https://python-binance.readthedocs.io/)
package, and to use it you need to create a Binance account, create an API key
and update the `binance.api.key` and `binance.api.secret` values in the config
file or through environment variables accordingly.

## Contributing

All contributions are welcome. You can submit any ideas or report bugs as
GitHub issues. If you'd like to improve code, fell free to open Pull Requests!

## License

Please, read our [LICENSE](LICENSE) file.
