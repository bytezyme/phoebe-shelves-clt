import argparse


def arg_parser():
    """ Parse command line arguments

    Outputs:
        Returns an object containing all command-line arguments
    """

    # Top Level Parser
    parser = argparse.ArgumentParser(prog='Owl Shelves CLT',
                                     description='CLT for managing a '
                                                 'book/reading database')

    subparsers = parser.add_subparsers(help="Top-level commands",
                                       dest='tool')

    # Add subparsers
    add_init_parser(subparsers)
    add_config_parser(subparsers)
    add_view_parser(subparsers)
    add_manage_parser(subparsers)

    return(parser.parse_args())


def add_init_parser(parser):
    """ Prepares database initialization parsers

    Args:
        parser {parser} -- Parent parser object

    Outputs:
        Adds init arguments to the parent argument parser
    """

    init_parser = parser.add_parser('init', help='Initialize database files')
    init_parser.add_argument('-p', '--path',
                             help='Initialize databases in specified PATH')

    init_parser.add_argument('-f', '--force',
                             action='store_true',
                             help='Force overwrite an existing database')


def add_config_parser(parser):
    """ Prepares configuration parsers

    Args:
        parser {parser} -- Parent parser object

    Outputs:
        Adds config arguments to the parent argument parser
    """

    config_parser = parser.add_parser('config',
                                      help='Update script configs, such '
                                           'as the data directory path')
    config_group = config_parser.add_mutually_exclusive_group()
    config_group.add_argument('-u', '--update', dest="path",
                              help='Update data directory to PATH')
    config_group.add_argument('-c', '--check', action='store_true',
                              help='Print out current data directory path')


def add_view_parser(parser):
    """ Prepares view module initialization parsers

    Args:
        parser {parser} -- Parent parser object

    Outputs:
        Adds view arguments to parent argument parser
    """

    view_parser = parser.add_parser('view', help='Visualize databases')
    add_db_parser(view_parser)

    # Add mode parser
    modes = ['table', 'charts', 'stats']
    modes_help = ('Print database as a [table], create [charts], or [analyze] '
                  'generate summary [stats]')
    view_parser.add_argument('mode', choices=modes, help=modes_help)


def add_manage_parser(parser):
    """ Prepares data management module initialization parsers

    Args:
        parser {parser} -- Parent parser object

    Outputs:
        Adds manage arguments to parent argument parser
    """

    management_parser = parser.add_parser('manage',
                                          help='Manage existing data')
    add_db_parser(management_parser)
    modes = ['add', 'edit', 'delete']
    modes_help = ('[Add] a new entry, [edit] an existing '
                  'entry, or [delete] and existing entry')
    management_parser.add_argument('mode', choices=modes, help=modes_help)


def add_db_parser(parser):
    """ Prepares database selection parsers

    Args:
        parser {parser} -- Parent parser object

    Outputs:
        Adds database selection argument to view or manage parser
    """

    db_choices = ['books', 'reading', 'authors', 'genres', 'series']
    db_help = 'Select which database to use the tools on'
    parser.add_argument("database", choices=db_choices, help=db_help)
