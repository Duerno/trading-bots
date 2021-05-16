Trading Bots
============

This repository implements an ever evolving set of simple trading bots
developed to autonomously trade inside general or cryptocurrency Exchanges,
such as Binance.

## Getting Started

### Requirements

- Python ([installation](https://www.python.org/downloads/))

All other utilities are automatically downloaded in the configuration process.

### Run Locally

First, you have to setup your host. Just run the following command to install
the library dependencies:

```sh
pip3 install -r requirements.txt
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

As an example, one can setup some settings, run the `bollinger` bot and set the
logging level as following:

```sh
export BOT_BINANCE_API_KEY=my-super-secret-api-key
export BOT_BINANCE_API_SECRET=my-super-secret-api-secret
python3 main.py --log-level=debug bollinger
```

Now, the chosen trading bot must be up and running. Enjoy!

### Test

Unfortunately, this project doesn't have any tests yet.

## Available Bots

Useful information about the available bots, how they work and their specific
settings.

### Bollinger Bot

Bollinger is a trading bot that uses Bollinger Bands to decide when to enter a
trade.

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
