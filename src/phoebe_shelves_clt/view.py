""" Launching point and supporting functions for database visualization tools.

This module serves as the launching point for the database visualization tools.
Backend-specific implementations are located within their specific modules and
common functions and methods are included in this file.
"""

from phoebe_shelves_clt.csv_backend import view_csv
from phoebe_shelves_clt.sql_backend import view_sql


def view_module(backend: str, db_select: str, mode, **kwargs):
    """ Launch visualization workflows

    Launch the visualization workflows for either the CSV or SQL backends

    Args:
        backend: Backend to use
        db_select: Database to manage
        mode: Visualization mode
    
    Keyword Args:
        data_directory (string): Path to CSV backend data directory
        sql_configs (Dict): SQL server configurations
    """
    if backend == "csv":
        view_csv.main(db_select, mode, kwargs["data_directory"])
    else:
        view_sql.main(db_select, mode, kwargs["sql_configs"])