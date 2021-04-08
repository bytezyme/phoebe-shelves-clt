"""Methods to read/write a configuration file.

This module provides methods for reading in a configuration file and saving
and updated configuration file to a given path using the configparser package.
"""

import configparser


def read_configs(config_path):
    """Read in a configuration file from a location.

    Args:
        config_path {string} -- Path to configuration file location

    Outputs:
        configs {configparser} -- Configurations
    """

    configs = configparser.ConfigParser()
    configs.read(config_path)
    return(configs)


def update_configs(config_path, update_dict):
    """Update and save a configuration file.

    Args:
        config_path {string} -- Path to configuration file location
        update_dict {dict} -- Dict containing updates in correct format

    Outputs:
        Saves the updated configuration file to the specified location
    """

    configs = configparser.ConfigParser()
    for section, key_value_dict in update_dict.items():
        configs[section] = key_value_dict

    with open(config_path, 'w') as config_file:
        configs.write(config_file)
