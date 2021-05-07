# External Packages
import os
import click

# Internal Modules
from .utils.config import read_configs, update_data_dir_path
from .modules.initialize import init_module
from .modules.manage import management_module
from .modules.view import view_module

# Common Option Sets
db_choice = click.argument("database", type=click.Choice(["reading", "books"],
                                                         case_sensitive=False))


@click.group()
@click.pass_context
def cli(ctx):
    """A command-line tool for tracking your reading!

    Owl Shelves CLT provides tools for tracking your reading based on two local
    CSV files.
    """
    # Ensure there's a dictionary if called directly
    ctx.ensure_object(dict)

    # Prepare overall configuration of the data directory
    # TODO: This needs to be generalized for distribution
    config_path = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'
    ctx.obj["cfg_path"] = config_path
    ctx.obj["cfgs"] = read_configs(config_path)


@cli.command()
@click.option("-f", "--force", is_flag=True)
@click.option("-p", "--path")
@click.pass_context
def init(ctx, force, path):
    """Initialize new databases.

    Create new databases in the specified data directory. If a path is not
    specified using PATH, then the script will use the path stored in the
    configuration file.

    \b
    Arguments:
        - [force]: Force-overwite an existing directory, if it exists.
        - [path]: New path to use and store in the configuration file.
    """

    # Switch to a new user-specified path if needed
    if path:
        update_data_dir_path(ctx.obj["cfg_path"], ctx.obj["cfgs"], path)
        ctx.obj["cfgs"]["PATHS"]["data_directory"] = path

    init_module(force, ctx.obj["cfgs"]["PATHS"]["data_directory"])


@cli.command()
@click.option("-c", "--check", is_flag=True,
              help="Print out the current database directory configuration.")
@click.option("-u", "--update",
              help="Update the database directory configuration to TEXT.")
@click.pass_context
def config(ctx, check, update):
    """Manage script configuration.

    Manages the script configurations stored in the confg.cfg file.
    """
    # Print out current data directory
    if check:
        data_directory = ctx.obj["cfgs"]["PATHS"]["data_directory"]
        print("Current data directory: {}".format(data_directory))

    # Update directory
    if update:
        print("Updated directory: {}".format(update))
        update_data_dir_path(ctx.obj["cfg_path"], ctx.obj["cfgs"], update)


@cli.command()
@db_choice
@click.argument("mode",
                type=click.Choice(["table", "graph", "analyze"],
                                  case_sensitive=False))
@click.pass_context
def view(ctx, database, mode):
    """View a database using different options.

    Visualize the database by 1) printing a table to the terminal,
    2) generating charts or graphs, and 3) generating summary statistics.

    \b
    Arguments
        - [reading|book]: Database to visualize
        - [table|graph|analyze]: Method of visualization
    """

    view_module(database, mode, ctx.obj["cfgs"]["PATHS"]["data_directory"])


@cli.command()
@db_choice
@click.argument("mode",
                type=click.Choice(["add", "edit", "delete"],
                                  case_sensitive=False))
@click.pass_context
def manage(ctx, database, mode):
    """Add, edit, or delete entries from a database.

    Modify the entries of a database by 1) adding a new entry, 2) editing
    an existing entry, or 3) deleting an existing entry.

    \b
    Arguments
        - [reading|book]: Database to visualize
        - [add|edit|delete]: Method of modification
    """
    management_module(database, mode,
                      ctx.obj["cfgs"]["PATHS"]["data_directory"])


if __name__ == "__main__":
    cli(obj={})
