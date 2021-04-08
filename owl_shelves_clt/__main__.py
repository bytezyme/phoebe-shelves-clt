#!/usr/bin/env python

import os

from .arg_parsing import arg_parser
from .config_utils import read_configs, update_configs
from .database_creation import init_module
from .data_management import management_module
from .data_view import view_module


def main():
    """Main program"""

    # TODO: This needs to be generalized for distirubtion
    config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'

    args = arg_parser()

    if args.action == 'init':

        # Use the user-specified path if passed, otherwise use default
        if args.path:
            new_configs = {'PATHS': {'data_directory': args.path}}
            update_configs(config_path, new_configs)

        # Initialize the databases
        configs = read_configs(config_path)
        init_module(args.force, configs.get('PATHS', 'data_directory'))

    elif args.action == 'config':
        if args.check:
            configs = read_configs(config_path)
            print('Directory Path: ' + configs.get('PATHS', 'data_directory'))
        else:
            if args.directory:
                new_configs = {'PATHS': {'data_directory': args.directory}}
            else:
                new_configs = {'PATHS': {'data_directory': 'data'}}

            update_configs(config_path, new_configs)

    elif args.action == 'view':
        configs = read_configs(config_path)
        view_module(args, configs.get('PATHS', 'data_directory'))

    elif args.action == 'manage':
        configs = read_configs(config_path)
        management_module(args, configs.get('PATHS', 'data_directory'))


def cli_entry_point():
    """Entry point for a command line call"""
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nClosing... No changes have been saved!")
        pass


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nClosing... No changes have been saved!")
        pass
