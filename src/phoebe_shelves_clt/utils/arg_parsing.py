""" Command-line argument parsing module

Provides command-line argument parsing functionality using argparse for the
initial user interface.
"""

import argparse

def arg_parser() -> argparse.Namespace:
    """ Parse command-line arguments

    Sets up and parses command-line arguments.

    Outputs:
        Returns an ArgumentParser containing all command-line arguments
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


def add_init_parser(subparser):
    """ Prepares backend initialization parser

    Prepares and adds all of the arguments for the init parser to the parent
    parser object.

    Args:
        subparser (Subparser): Parent subparser object
    """
    init_parser = subparser.add_parser("init", help='Initialize backend files')
    init_parser.add_argument("-p", "--path",
                             help="Initialize backend files at specified PATH")

    init_parser.add_argument("-f", "--force",
                             action="store_true",
                             help="Force overwrite an existing database")


def add_config_parser(subparser):
    """ Prepares configuration mode control parser

    Prepares and adds all of the argumnts for the configuration parser to the
    parent parser object.

    Args:
        subparser (Subparser): Parent parser object
    """
    cfg_parser = subparser.add_parser("config", 
                                      help="Update script configurations")
    cfg_subparser = cfg_parser.add_subparsers(help="Check or update configs",
                                              dest="config_mode")

    backend_parser = cfg_subparser.add_parser("backend",
                                              help="Set CSV or SQL backend.")
    backend_parser.add_argument("backend", choices=["csv", "sql"],
                                help="Select backend choice.")

    cfg_subparser.add_parser("check", help="Print out current configurations.")

    data_dir_parser = cfg_subparser.add_parser("data_dir",
                                               help="Set data directory.")
    data_dir_parser.add_argument("path", help="Path to data directory.")

    database_parser = cfg_subparser.add_parser("database",
                                               help="Set database name.")
    database_parser.add_argument("name", help="Name of SQL database.")

    user_parser = cfg_subparser.add_parser("user",
                                           help="Set PostgreSQL username.")
    user_parser.add_argument("user", help="PostgreSQL username.")

    host_parser = cfg_subparser.add_parser("host", help="Set PostgreSQL host.")
    host_parser.add_argument("host", help="PostgreSQL host.")


def add_view_parser(subparser):
    """ Prepares view module mode control parser

    Prepares and adds the view module mode control arguments to the parent
    parser object.

    Args:
        subparser (Subparser): Parent parser object
    """
    view_parser = subparser.add_parser("view", help="Visualize databases")
    add_db_arguments(view_parser)

    # Add mode parser
    modes = ["table", "charts", "stats"]
    modes_help = ("Print database as a [table], create [charts], or [analyze] "
                  "generate summary [stats] ")
    view_parser.add_argument("mode", choices=modes, help=modes_help)


def add_manage_parser(subparser):
    """ Prepares data manage module mode control parser

    Prepares and adds the manage module mode control arguments to the parent
    parser object.

    Args:
        subparser (Subparser): Parent parser object
    """
    management_parser = subparser.add_parser("manage",
                                             help="Manage existing data")
    add_db_arguments(management_parser)
    modes = ["add", "edit", "delete"]
    modes_help = ("[Add] a new entry, [edit] an existing "
                  "entry, or [delete] and existing entry")
    management_parser.add_argument("mode", choices=modes, help=modes_help)


def add_db_arguments(parser):
    """ Prepares database selection arguments

    Prepares and adds the database selection arguments to the view or manage
    parsers.

    Args:
        parser (Parser): Parent parser object
    """

    db_choices = ["books", "reading", "authors", "genres", "series"]
    db_help = "Select which database to use the tools on"
    parser.add_argument("database", choices=db_choices, help=db_help)
