"""Methods to read/write a configuration file.

This module provides methods for reading in a configuration file and saving
and updated configuration file to a given path using the configparser package.
"""

import configparser
import os


def create_configs(config_path):
    """Initialize configuration file

    Args:
        config_path {string} -- Path to configuration file

    Outputs:
        configs {configparser} -- Configurations
    """

    configs = configparser.ConfigParser()

    # TODO: Have more generalized default data directory
    configs["GENERAL"] = {"backend": "csv"}
    configs["CSV"] = {"data_directory": "data"}  # Default
    configs["SQL"] = {"database": "phoebe_shelves_dev",
                      "user": "anthonyagbay",
                      "host": "localhost",
                      "export": "data"}

    with open(config_path, 'w') as config_file:
        configs.write(config_file)
    return(configs)


def read_configs(config_path):
    """Read in a configuration file from a location.

    Args:
        config_path {string} -- Path to configuration file location

    Outputs:
        configs {configparser} -- Configurations
    """

    if not os.path.isfile(config_path):
        configs = create_configs(config_path)
    else:
        configs = configparser.ConfigParser()
        configs.read(config_path)

    return(configs)


def update_data_dir(config_path, configs, new_path):
    """Update and save a configuration file.

    Args:
        config_path {string} -- Path to configuration file location
        configs {configparser} -- Configurations
        new_path {string} -- New data directory path

    Outputs:
        configs -- Configurations with updated data directory path
        Also aves the updated configuration file to the specified location
    """

    configs['PATHS']['data_directory'] = new_path
    with open(config_path, 'w') as config_file:
        configs.write(config_file)
    return(configs)
