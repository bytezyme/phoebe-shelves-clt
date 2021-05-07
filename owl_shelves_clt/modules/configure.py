"""Methods to read/write a configuration file.

This module provides methods for reading in a configuration file and saving
and updated configuration file to a given path using the configparser package.
"""

import configparser
import os


def create_configs(config_path):
    """
    """

    configs = configparser.ConfigParser()

    # TODO: Have more generalized default data directory
    configs['PATHS'] = {'data_directory': 'data'}  # Default

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
        update_dict {dict} -- Dict containing updates in correct format

    Outputs:
        Saves the updated configuration file to the specified location
    """

    configs['PATHS']['data_directory'] = new_path
    with open(config_path, 'w') as config_file:
        configs.write(config_file)
    return(configs)
