#!/usr/bin/env python

import os

from .utils.arg_parsing import arg_parser
from .configure import read_configs, update_data_dir
from .initialize import init_module
from .manage import management_module
from .view import view_module


def main():
    """Main program"""

    # TODO: This needs to be generalized for distirubtion
    # Configuration and argument parsing
    config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
    configs = read_configs(config_path)
    args = arg_parser()

    if args.tool == 'init':
        if args.path:
            configs = update_data_dir(config_path, configs, args.path)
        init_module(args.force, configs.get('PATHS', 'data_directory'))

    elif args.tool == 'config':
        if args.check:
            print('Data Directory: ', configs.get('PATHS', 'data_directory'))
        elif args.path:
            update_data_dir(config_path, configs, args.path)

    elif args.tool == 'view':
        view_module(args.database, args.mode,
                    configs.get('PATHS', 'data_directory'))

    elif args.tool == 'manage':
        management_module(args.database, args.mode,
                          configs.get('PATHS', 'data_directory'))


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
