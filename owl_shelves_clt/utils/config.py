"""Methods to read/write a configuration file.

This module provides methods for reading in a configuration file and saving
and updated configuration file to a given path using the configparser package.
"""

import configparser
import os


def read_configs(config_path):
    """Read in a configuration file from a location.

    Args:
        config_path {string} -- Path to configuration file

    Outputs:
        configs {configparser} -- Configurations
    """

    if not os.path.isfile(config_path):
        configs = create_configs(config_path)
    else:
        configs = configparser.ConfigParser()
        configs.read(config_path)

    return(configs)


def create_configs(config_path):
    """Create new configuration file if none exists

    Args:
        config_path {string} -- Path to configuration file

    Returns:
        configs {configparser} -- Configurations
    """

    configs = configparser.ConfigParser()
    configs["PATHS"] = {'data_directory': 'data'}

    with open(config_path, 'w') as config_file:
        configs.write(config_file)
    return(configs)


def update_data_dir_path(config_path, configs, new_dir_path):
    """Update and save a configuration file.

    Args:
        config_path {string} -- Path to configuration file
        configs {configparser} -- Current script configurations
        new_dir_path {string} -- New data directory path

    Outputs:
        Updates the "data_directory" field of the configuration file
    """

    configs["PATHS"]["data_directory"] = new_dir_path
    with open(config_path, 'w') as config_file:
        configs.write(config_file)
