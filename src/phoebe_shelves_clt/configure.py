""" Methods to read/write a configuration file.

This module provides methods for reading in a configuration file and saving
and updated configuration file to a given path using the configparser package.
"""

import os
import configparser

def create_configs(config_path: str) -> configparser.ConfigParser:
    """ Initialize configuration file

    Initializes the configuration file with default values for each
    configurable property.

    Args:
        config_path: Path to configuration file

    Returns:
        configs: Script configurations

    Todo:
        * Implement additional SQL configurations
        * Implement more generalized default data directory
    """

    configs = configparser.ConfigParser()

    # TODO: Have more generalized default data directory
    configs["GENERAL"] = {"backend": "csv",
                          "data_directory": "data"}

    configs["SQL"] = {"database": "phoebeshelves",
                      "user": "postgres",
                      "host": "localhost"}

    with open(config_path, 'w') as config_file:
        configs.write(config_file)
    return(configs)


def read_configs(config_path: str) -> configparser.ConfigParser:
    """ Read in a configuration file from a location.

    Read in the configurations from the config.cfg file from the given
    location.

    Args:
        config_path: Path to configuration file location

    Outputs:
        configs: Script configurations
    """

    if not os.path.isfile(config_path):
        configs = create_configs(config_path)
    else:
        configs = configparser.ConfigParser()
        configs.read(config_path)

    return(configs)

def print_configs(configs: configparser.ConfigParser):
    """ Print out all config properties

    Print out each section and its configuration properties for inspection on
    the command-line.

    Args:
        configs: Script configurations
    """
    for section in configs.sections():
        print(section)
        for prop, val in configs.items(section):
            print(f"{prop}: {val}")
        print("")


def update_config(config_path: str, configs: configparser.ConfigParser,
                  config_name: str, new_val: str):
    """ Updates a configurable property to a new value

    Update a configurable property to the user-provided value. This function
    will also save the updated configurations to the file as well as return
    the updated configurations for additional use, if needed.

    Args:
        config_path: Path to the config.cfg file
        configs: Old script configurations
        config_name: Configuration property to update
        new_val: New value of the configuration property

    Returns:
        configs: Updated script configurations

    """
    if config_name in {"backend", "data_directory"}:
        section = "GENERAL"
    else:
        section = "SQL"
    configs[section][config_name] = new_val
    with open(config_path, "w") as config_file:
        configs.write(config_file)
    return(configs)
