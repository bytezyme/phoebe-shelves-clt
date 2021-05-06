import os
import click


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
    """Manage tool configurations.
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
                type=click.Choice(["print", "graph", "analyze"],
                                  case_sensitive=False))
@click.pass_context
def view(ctx, database, mode):
    """Visualize a database using different options.
    
    \b
    [reading|book]: Database to visualize
    
    \b
    [print|graph|analyze]: Method of visualization
        - print: Print table to command-line
        - graph: Generate charts using plotting modules
        - analyze: Generate summary/aggregate statistics
    """
    view_module(database, mode, ctx.obj["cfgs"]["PATHS"]["data_directory"])


@cli.command()
@db_choice
@click.argument("mode",
              type=click.Choice(["add", "edit", "delete"], 
                                case_sensitive=False))
@click.pass_context
def manage(ctx,database, mode):
    """Add, edit, or delete entries from a database.
    """
    management_module(database, mode, ctx.obj["cfgs"]["PATHS"]["data_directory"])


if __name__ == "__main__":
    cli(obj={})