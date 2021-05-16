Trading Bots
============

This repository implements an ever evolving set of simple trading bots
developed to autonomously trade inside general or crypto-currency Exchanges,
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

To check the available bots and options, run the following command:

```sh
python3 main.py
```

One can customize the bots settings by either updating the
`config/default.yaml` file or defining environment variables. So that
variables can replace the config file settings, they must be all capitalized,
prefixed with `BOT_` and each different YAML hierarchy level must be separated
by an `_`.

As an example, one can setup some settings, run the `bellinger` bot and set the
logging level as following:

```sh
export BOT_BINANCE_API_KEY=my-super-secret-api-key
export BOT_BINANCE_API_SECRET=my-super-secret-api-secret
python3 main.py --log-level=debug bollinger
```

Now, the chosen trading bot must be up and running. Enjoy!

### Test

TODO.

### Build and Deploy

TODO.
