#!/usr/bin/env python

""" Main program for running the command line tools

TODO
    * 
"""

import os

from phoebe_shelves_clt.utils.arg_parsing import arg_parser
from phoebe_shelves_clt import manage
from phoebe_shelves_clt import initialize
from phoebe_shelves_clt import view
from phoebe_shelves_clt import configure


def main():
    """ Main program"""

    # TODO: This needs to be generalized for distirubtion
    config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
    configs = configure.read_configs(config_path)
    args = arg_parser()

    # Configuration is not dependent on the backend, so can be treated separately
    if args.tool == "config":
        if args.check:
            print('Data Directory: ', configs.get('CSV', 'data_directory'))
        elif args.path:
            configure.update_data_dir(config_path, configs, args.path)
    
    else:
        if configs.get("GENERAL", "backend") == "csv":
            if args.tool == 'init':
                if args.path:
                    configs = configure.update_data_dir(config_path, configs, args.path)
                initialize.init_module("csv", args.force, data_directory=configs.get('CSV', 'data_directory'))
            elif args.tool == "view":
                view.view_module("csv", args.database, args.mode, data_directory=configs["CSV"]["data_directory"])
            elif args.tool == "manage":
                manage.manage_module("csv", args.database, args.mode, data_directory=configs["CSV"]["data_directory"])
        else:
            if args.tool == "init":
                initialize.init_module("sql", args.force,
                                    sql_configs=dict(configs["SQL"]))
            elif args.tool == "view":
                view.view_module("sql", args.database, args.mode,
                                sql_configs=dict(configs["SQL"]))
            elif args.tool == "manage":
                manage.manage_module("sql", args.database, args.mode,
                                    sql_configs=dict(configs["SQL"]))


def cli_entry_point():
    """ Entry point for a command line call"""
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
