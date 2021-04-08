import argparse


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
                                       dest='action')

    subparsers = add_init_parser(subparsers)
    subparsers = add_config_parser(subparsers)
    subparsers = add_view_parser(subparsers)
    subparsers = add_management_parser(subparsers)

    arguments = parser.parse_args()
    return(arguments)


def add_init_parser(parser):
    init_parser = parser.add_parser('init', help='Initialize database files')
    init_parser.add_argument('-p', '--path',
                             help='Path to database directory')

    init_parser.add_argument('-f', '--force',
                             action='store_true',
                             help='Force overwrite an existing database')
    return(parser)


def add_config_parser(parser):
    config_parser = parser.add_parser('config',
                                      help='Update script configs, such '
                                           'as the data directory path')

    config_parser.add_argument('-d', '--directory',
                               help='Path to database directory')

    config_parser.add_argument('-c', '--check', action='store_true',
                               help='Print out current data directory path')
    return(parser)


def add_view_parser(parser):
    view_parser = parser.add_parser('view', help='Visualize databases')
    view_parser = add_db_parser(view_parser)

    # Add mode parser
    modes = ['print', 'graph', 'analyze']
    modes_help = ('Indicate whether to [print] to the console, [graph] using '
                  'plotting libaries or [analyze] aggregate details.')
    view_parser.add_argument('-m', '--mode', choices=modes, help=modes_help)
    return(parser)


def add_management_parser(parser):
    management_parser = parser.add_parser('manage',
                                          help='Manage existing data')

    management_parser = add_db_parser(management_parser)

    # Add mode parser
    modes = ['add', 'edit', 'delete']
    modes_help = ('Indicate whether to [add] a new entry, [edit] an existing '
                  'entry, or [delete] and existing entry.')
    management_parser.add_argument('-m', '--mode', choices=modes,
                                   help=modes_help)

    return(parser)


def add_db_parser(parser):
    db_group = parser.add_mutually_exclusive_group()
    db_group.add_argument('-bd', '--booksdb',
                          action='store_true',
                          help='Flag to indicate access to book database')

    db_group.add_argument('-rd', '--readingdb',
                          action='store_true',
                          help='Flag to indicate access to the reading '
                               'events database')
    return(parser)