"""Methods to read/write a configuration file.

This module provides methods for reading in a configuration file and saving
and updated configuration file to a given path using the configparser package.
"""

import configparser
import os


def read_configs(config_path):
    """Read in a configuration file from a location.
    
    TODO: Update this section

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

def create_configs(config_path):
    """Create new configuration file if none exists
    
    TODO: Update this section
    
    """
    configs = configparser.ConfigParser()
    configs["PATHS"] = {'data_directory': 'data'}
    
    with open(config_path, 'w') as config_file:
        configs.write(config_file)
    
    return(configs)
    

def update_data_dir_path(config_path, configs, new_dir_path):
    """Update and save a configuration file.
    
    TODO: Update this section

    Args:
        config_path {string} -- Path to configuration file location
        update_dict {dict} -- Dict containing updates in correct format

    Outputs:
        Saves the updated configuration file to the specified location
    """

    configs["PATHS"]["data_directory"] = new_dir_path
    with open(config_path, 'w') as config_file:
        configs.write(config_file)
