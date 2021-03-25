import argparse
import pandas as pd
import os
import configparser
from data_management import create_databases, update_book_db, update_reading_db
from data_view import print_db

# General Use Constants
config_path = "code/configs.conf"

def read_configs():
    """ Read in configurations from the config file

    Outputs:
        config {ConfigParser} -- Contains saved configurations for the program
    """

    config = configparser.ConfigParser()
    config.read(config_path)
    return(config)

def write_configs(data_path):
    """ Write out configurations to the config file
    
    # TODO: May need to make more general

    Inputs:
        data_path {string} -- Locatin of the new data directory

    Outputs:
        Saves updated config file to the config_path
    """

    config = configparser.ConfigParser()
    config['PATHS'] = {'data_directory': data_path}
    with open (config_path, 'w') as config_file:
        config.write(config_file)

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
    
    ## Initialization Parser
    init_parser = subparsers.add_parser('init',
                                        help='Use to create new databases')

    init_parser.add_argument('-p', '--path', 
                             help='Path to database directory')

    init_parser.add_argument('-f', '--force',
                             action='store_true',
                             help='Force overwrite an existing database')

    ## Configuration Parser
    config_parser = subparsers.add_parser('config',
                                          help='Update script configs, such '
                                               'as the data directory path')

    config_parser.add_argument('-d', '--directory',
                               help='Path to database directory')

    ## Access Parser
    view_parser = subparsers.add_parser('view',
                                        help='Visualize databases')

    ### Initial Separation
    view_parser.add_argument('-bd', '--booksdb',
                             action='store_true', 
                             help='Flag to indicate access to book database')

    view_parser.add_argument('-rd', '--readingdb', 
                             action='store_true',
                             help='Flag to indicate access to the reading '
                                    'events database')

    ### Actions
    view_parser.add_argument('-p', '--print',
                             action='store_true',
                             help='Indicates to print the details')

    ## Management Parser
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
    """ Main program
    """
    args = arg_parser()
    if args.mode == 'init':

        # Use the user-specified path if passed, otherwise use default
        if args.path:
            write_configs(args.path)

        # Initialize the databases
        create_databases(args.force,
                         read_configs().get('PATHS','data_directory'))

    elif args.mode == 'config':
        # User specifies update to data_directory
        if args.directory:
            write_configs(args.directory)
        else:
            write_configs('data')

    elif args.mode == 'view':
        # Setup source database
        database_path = read_configs().get('PATHS', 'data_directory') + '/'
        if args.booksdb:
            database_path += 'books.csv'
        elif args.readingdb:
            database_path += 'reading.csv'

        # Run Action
        if args.print:
            print_db(database_path)

    elif args.mode =='manage':
        if args.booksdb: 
            update_book_db(read_configs().get('PATHS', 'data_directory'))
        elif args.readingdb:
            update_reading_db(read_configs().get('PATHS', 'data_directory'))
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nClosing...")
        pass