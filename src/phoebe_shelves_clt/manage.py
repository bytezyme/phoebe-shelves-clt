""" Launching point and supporting functions for database management tools.

This module serves as the launching point for the database management tools.
Backend-specific implementations are located within their specific modules and
common functions and methods are included in this file.
"""

import numpy as np

from phoebe_shelves_clt.csv_backend import manage_csv
from phoebe_shelves_clt.sql_backend import manage_sql
from phoebe_shelves_clt.utils import data_model

def prompt_for_rating(prompt: str):
    """Prompt user for an integer rating (max 5).

    Args:
        prompt: Prompt that user sees on the command line

    Outputs:
        rating (int | float): Intger rating or np.nan if empty string is passed
    """

    rating = input(prompt)

    while rating not in {"", "1", "2", "3", "4", "5"}:
        rating = input("Choose an integer between 1 and 5 or leave blank: ")

    # Format rating
    rating = int(rating) if rating != "" else np.nan
    return(rating)


def manage_module(backend: str, db_select: str, mode: str, **kwargs):
    """ Launch management workflows for either backend

    Launch the mangement workflows for either the CSV or SQL backends

    Args:
        backend: Backend to use
        db_select: Database to manage
        mode: Management mode
    
    Keyword Args:
        data_directory (string): Path to CSV backend data directory
        sql_configs (Dict): SQL server configurations
    """
    if backend == "csv":
        model = data_model.CSVDataModel(kwargs["data_directory"])
        manage_csv.main(db_select, mode, model)
    else:
        manage_sql.main(db_select, mode, kwargs["sql_configs"])