#!/usr/bin/env python

import argparse
from config_utils import read_configs, update_configs

from database_creation import init_databases
from data_management import update_book_db, update_reading_db
from data_view import view_module


def arg_parser():
    """ Parse command line arguments

    Outputs:
        arguments {object} -- object containing command line arguments
    """

    # Top Level Parser
    parser = argparse.ArgumentParser(prog='Owl Shelves CLT',
                                     description='CLT for managing a '
                                                 'book/reading database')
    subparsers = parser.add_subparsers(help="Top-level commands",
                                       dest='mode')

    # Initialization Parser
    init_parser = subparsers.add_parser('init',
                                        help='Use to create new databases')

    init_parser.add_argument('-p', '--path',
                             help='Path to database directory')

    init_parser.add_argument('-f', '--force',
                             action='store_true',
                             help='Force overwrite an existing database')

    # Configuration Parser
    config_parser = subparsers.add_parser('config',
                                          help='Update script configs, such '
                                               'as the data directory path')

    config_parser.add_argument('-d', '--directory',
                               help='Path to database directory')

    # Access Parser
    view_parser = subparsers.add_parser('view',
                                        help='Visualize databases')

    # Initial Separation
    view_parser.add_argument('-bd', '--booksdb',
                             action='store_true',
                             help='Flag to indicate access to book database')

    view_parser.add_argument('-rd', '--readingdb',
                             action='store_true',
                             help='Flag to indicate access to the reading '
                                    'events database')

    # Actions
    view_parser.add_argument('-p', '--print',
                             action='store_true',
                             help='Indicates to print the details')

    # Management Parser
    management_parser = subparsers.add_parser('manage',
                                              help='Manage existing data')

    # Initial Separation
    management_parser.add_argument('-bd', '--booksdb',
                                   action='store_true',
                                   help='Flag to indicate change to '
                                        'the book database')

    management_parser.add_argument('-rd', '--readingdb',
                                   action='store_true',
                                   help='Flag to indicate change to '
                                        'the reading database')

    arguments = parser.parse_args()
    return(arguments)


def main():
    """Main program"""
    config_path = 'setup.cfg'
    args = arg_parser()

    if args.mode == 'init':

        # Use the user-specified path if passed, otherwise use default
        if args.path:
            updated_configs = {'PATHS': {'data_directory': args.path}}
            update_configs(config_path, updated_configs)

        # Initialize the databases
        configs = read_configs(config_path)
        init_databases(args.force, configs.get('PATHS', 'data_directory'))

    elif args.mode == 'config':
        # User specifies update to data_directory
        if args.directory:
            updated_configs = {'PATHS': {'data_directory': args.directory}}
        else:
            updated_configs = {'PATHS': {'data_directory': 'data'}}

        update_configs(config_path, updated_configs)

    elif args.mode == 'view':
        configs = read_configs(config_path)
        view_module(args, configs.get('PATHS', 'data_directory'))

    elif args.mode == 'manage':
        configs = read_configs(config_path)
        if args.booksdb:
            update_book_db(configs.get('PATHS', 'data_directory'))
        elif args.readingdb:
            update_reading_db(configs.get('PATHS', 'data_directory'))


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nClosing... No changes have been saved!")
        pass
