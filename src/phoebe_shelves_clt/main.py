#!/usr/bin/env python
""" Main program for running the command-line tools

Main entry point and logic for running the command-line tools.
"""

import os

from phoebe_shelves_clt.utils.arg_parsing import arg_parser
from phoebe_shelves_clt import manage
from phoebe_shelves_clt import initialize
from phoebe_shelves_clt import view
from phoebe_shelves_clt import configure
from phoebe_shelves_clt.utils import data_model


def main():
    """ Main program"""

    # TODO: This needs to be generalized for distirubtion
    config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
    configs = configure.read_configs(config_path)
    args = arg_parser()

    # Configuration is not dependent on the backend, so can be treated separately
    if args.tool == "config":
        if args.config_mode == "check":
            configure.print_configs(configs)
        elif args.config_mode == "backend":
            configure.update_config(config_path, configs, "backend", args.backend)
        elif args.config_mode == "data_dir":
            configure.update_config(config_path, configs,"data_directory", args.path)
        elif args.config_mode == "database":
            configure.update_config(config_path, configs, "database", args.name)
        elif args.config_mode == "user":
            configure.update_config(config_path, configs, "user", args.user)
        elif args.config_mode == "host":
            configure.update_config(config_path, configs, "host", args.host)
    
    else:
        if configs.get("GENERAL", "backend") == "csv":
            if args.tool == "init":
                if args.path:
                    configs = configure.update_config(config_path, configs,
                                                    "data_dir", args.path)
                data_dir = configs.get("GENERAL", "data_directory")
                initialize.init_module("csv", args.force,
                                        data_directory=data_dir)
            elif args.tool == "view":
                data_dir = configs.get("GENERAL", "data_directory")
                view.view_module("csv", args.database, args.mode,
                                 data_directory=data_dir)
            elif args.tool == "manage":
                data_dir = configs.get("GENERAL", "data_directory")
                manage.manage_module("csv", args.database, args.mode,
                                     data_directory=data_dir)
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
