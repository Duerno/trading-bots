import click
import os
import yaml
import logging


def execute():
    add_subcommands()
    entry_point(obj={})


@click.group()
@click.option('--log-level', default='info', help='Set the logging level. (default: info, options: debug|info|warning|error)')
@click.option('--config-file', default='config/default.yaml', help='Set the YAML config file. (default: config/default.yaml)')
@click.pass_context
def entry_point(ctx, log_level, config_file):
    """
    Hey, welcome! This project aims to provide a set of simple trading bots
    developed to autonomously trade inside general or cryptocurrency Exchanges,
    such as Binance.
    """
    setup_logging(log_level)
    ctx.obj['config'] = parse_config(config_file)


def add_subcommands():
    from . import serial_trader
    from . import parallel_trader
    modules = (
        serial_trader,
        parallel_trader,
    )
    for mod in modules:
        for attr in dir(mod):
            foo = getattr(mod, attr)
            if callable(foo) and type(foo) is click.core.Command:
                entry_point.add_command(foo)


def setup_logging(log_level):
    format = '%(levelname)s\t%(asctime)s %(message)s'
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('invalid log level: %s' % log_level)
    logging.basicConfig(encoding='utf-8', format=format, level=numeric_level)


def parse_config(filename, env_vars_prefix='bot'):
    """
    Load a yaml configuration file and resolve any environment variables.
    """
    if not os.path.isfile(filename):
        raise ValueError('invalid filename: %s' % filename)

    config = None
    with open(filename) as data:
        config = yaml.load(data, yaml.loader.SafeLoader)

    def update_config_with_env_vars(config, config_name, env_var_separator='_'):
        if config == None:
            return config

        if type(config) == dict:
            for node in config:
                config[node] = update_config_with_env_vars(
                    config[node], '{}.{}'.format(config_name, node))
            return config

        env_var_name = config_name.upper().replace('.', env_var_separator)
        return os.environ.get(env_var_name) or config

    return update_config_with_env_vars(config, env_vars_prefix)
