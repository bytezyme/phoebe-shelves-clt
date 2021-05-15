#!/usr/bin/env python

import os

from .utils.arg_parsing import arg_parser
from .configure import read_configs, update_data_dir
from .initialize import init_module, init_sql
from .manage import management_module
from .view import view_module
from .sql.manage_sql import manage_sql
from .sql.view_sql import view_sql


def main():
    """Main program"""

    # TODO: This needs to be generalized for distirubtion
    # Configuration and argument parsing
    config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
    configs = read_configs(config_path)
    args = arg_parser()

    # Initialization and Configuration


    # Main Tools
    #! Temporarily split
    # TODO: Simplify once the sql backend is done
    if configs.get("GENERAL", "backend") == "csv":
        if args.tool == 'init':
            if args.path:
                configs = update_data_dir(config_path, configs, args.path)
            init_module(args.force, configs.get('CSV', 'data_directory'))
        elif args.tool == 'config':
            if args.check:
                print('Data Directory: ', configs.get('CSV', 'data_directory'))
            elif args.path:
                update_data_dir(config_path, configs, args.path)
        if args.tool == "view":
            view_module(args.database, args.mode,
                        configs["CSV"]["data_directory"])
        elif args.tool == "manage":
            management_module(args.database, args.mode,
                              configs["CSV"]["data_directory"])
    else:
        if args.tool == "init":
            init_sql(args.force, dict(configs["SQL"]))
        elif args.tool == "view":
            view_sql(args.database, args.mode, dict(configs["SQL"]))
        elif args.tool == "manage":
            manage_sql(args, configs)


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
