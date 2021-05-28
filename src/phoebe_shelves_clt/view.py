""" Launching point and supporting functions for database visualization tools.

This module serves as the launching point for the database visualization tools.
Backend-specific implementations are located within their specific modules and
common functions and methods are included in this file.
"""

from typing import Union, Callable
import pandas as pd

from phoebe_shelves_clt.utils import data_model
from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.sql_backend import queries
from phoebe_shelves_clt.csv_backend import view_csv
from phoebe_shelves_clt.sql_backend import view_sql

DataFrame = pd.DataFrame

def retrieve_filter_function(backend: str, table: str, *args) -> Callable:
    """ Retrieve the correct filter function

    Retrieves the correct filter function for the backend-table combination.
    This allows for a single generic filter helper function for both backends.

    Args:
        backend: Flag to run the SQL or CSV backend functions.
        table: Name of the table to filter.
    
    Optional Args:
        CSVDataModel: CCSVDataModel instance for the CSV backend.

    Returns:
        filter_function: Underlying function to generate the final filter for
            either backend data models.
    """
    if backend == "csv":
        if table == "reading":
            filter_function = args[0].generate_main_reading
        else:
            filter_function = args[0].generate_main_books
    else:
        if table == "reading":
            filter_function = queries.main_reading_query
        else:
            filter_function = queries.main_books_query
    return(filter_function)

def numeric_filter(table: str, column: str, backend: str, **kwargs) -> Union[str, DataFrame]:
    """ Use numerical thresholds to filter a table

    Prompts the user to 1) select a type of numerical comparison and 2) the
    thresholds to use for the comparison. It then runs the appropriate filter
    functions to generate either 1) the SQL query with the filter or 2) the 
    pandas filtering statements.

    Args:
        table: Name of the table to filter.
        column: Name of the column to filter on.
        backend: Flag to run the SQL or CSV backend functions.
    
    Keyword Args:
        model (CSVDataModel): CSVDataModel instance for the CSV backend.

    Returns:
        Depending on the backend, this function returns two types of values:
            (str): SQL query string that will be executed later.
            (CSVDataModel): User-friendly DataFrame representation that has
                been filtered appropriately.
    """
    threshold_prompt = ("Would you like to filter based on a [1] ≤ threshold, "
                        "[2] ≥ threshold, [3] range, or [4] missing values?: ")
    threshold_mode = inputs.prompt_from_choices([1,2,3,4], threshold_prompt)
    lower_thresh_prompt = "What's the smallest value (inclusive)?: "
    upper_thresh_prompt = "What's the largest_value (inclusive)?: "

    if backend == "csv":
        filter_function = retrieve_filter_function(backend, table, kwargs["model"])
    else:
        filter_function = retrieve_filter_function(backend, table)

    if threshold_mode == 1:
        lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        return(filter_function(column, comp_type=threshold_mode,
                               thresholds=[lower_thresh]))
    elif threshold_mode == 2:
        upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        return(filter_function(column, comp_type=threshold_mode,
                              thresholds=[upper_thresh]))
    elif threshold_mode == 3:
        lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        return(filter_function(column, comp_type=threshold_mode,
                              thresholds=[lower_thresh, upper_thresh]))
    else:  # threshold_mode == 4
        return(filter_function(column, comp_type=threshold_mode, thresholds=[]))

def date_filter(table: str, column: str, backend: str, **kwargs) -> Union[str, DataFrame]:
    """ Use date-based thresholds to filter a table

    Prompts the user to 1) select a type of date-based comparison and 2) the
    thresholds to use for the comparison. It then runs the appropriate filter
    functions to generate either 1) the SQL query with the filter or 2) the 
    pandas filtering statements.

    Args:
        table: Name of the table to filter.
        column: Name of the column to filter on.
        backend: Flag to run the SQL or CSV backend functions.
    
    Keyword Args:
        model (CSVDataModel): CSVDataModel instance for the CSV backend.

    Returns:
        Depending on the backend, this function returns two types of values:
            (str): SQL query string that will be executed later.
            (CSVDataModel): User-friendly DataFrame representation that has
                been filtered appropriately.
    """ 
    threshold_prompt = ("Would you like to filter based on an [1] earliest date "
                        "(anytime after), [2] latest date (anytime before), "
                        "[3] range of dates, [4] specific year, or [5] "
                        "missing dates?: ")
    threshold_mode = inputs.prompt_from_choices([1,2,3,4,5], threshold_prompt)
    early_date_prompt = "What's the earliest date (inclusive)?: "
    late_date_prompt = "What's the latest date (inclusive)?: "
    year_prompt = "What year would you like to view?: "

    if backend == "csv":
        filter_function = retrieve_filter_function(backend, table, kwargs["model"])
        as_string = False  # Need to set different prompt_for_date formats
    else:
        filter_function = retrieve_filter_function(backend, table)
        as_string = True

    if threshold_mode == 1:
        early_date = inputs.prompt_for_date(early_date_prompt,
                                            as_string=as_string)
        return(filter_function(column, comp_type=threshold_mode,
                              thresholds=[early_date]))
    elif threshold_mode == 2:
        late_date = inputs.prompt_for_date(late_date_prompt,
                                           as_string=as_string)
        return(filter_function(column, comp_type=threshold_mode,
                              thresholds=[late_date]))
    elif threshold_mode == 3:
        early_date = inputs.prompt_for_date(early_date_prompt,
                                            as_string=as_string)
        late_date = inputs.prompt_for_date(late_date_prompt,
                                           as_string=as_string)
        return(filter_function(column, comp_type=threshold_mode,
                              thresholds=[early_date, late_date]))
    elif threshold_mode == 4:
        year = inputs.prompt_for_date(year_prompt, as_string=as_string)
        return(filter_function(column, comp_type=threshold_mode,
                              thresholds=[year]))

    else:
        return(filter_function(column, comp_type=threshold_mode, thresholds=[]))


def options_filter(table: str, column: str, backend: str, **kwargs) -> Union[str, DataFrame]:
    """ Use options-based thresholds to filter a table

    Prompts the user to select from a list of options to filter on. This is
    primarily used to filter categorical data like author names, titles, and
    genres. It then runs the appropriate filter functions to generate either 1)
    the SQL query with the filter or 2) the pandas filtering statements.

    Args:
        table: Name of the table to filter.
        column: Name of the column to filter on.
        backend: Flag to run the SQL or CSV backend functions.
    
    Keyword Args:
        model (CSVDataModel): CSVDataModel instance for the CSV backend.
        conn (psycopg2.connection): Connection to the PostgreSQL database.

    Returns:
        Depending on the backend, this function returns two types of values:
            (str): SQL query string that will be executed later.
            (CSVDataModel): User-friendly DataFrame representation that has
                been filtered appropriately.
    """ 
    if backend == "csv":
        filter_function = retrieve_filter_function(backend, table, kwargs["model"])

        if column == "Title":
            opts_dict = kwargs["model"].get_books_dict()
        elif column == "Author":
            opts_dict = kwargs["model"].get_authors_dict()
        else:
            opts_dict = kwargs["model"].get_genres_dict()
    else:
        filter_function = retrieve_filter_function(backend, table)

        if column == "Title":
            opts_dict = queries.retrieve_books_list(kwargs["conn"])
        elif column == "Author":
            opts_dict = queries.retrieve_authors_list(kwargs["conn"])
        else:
            opts_dict = queries.retrieve_genres_list(kwargs["conn"])

    id_list = []
    print(f"\nChoose from the {column.lower()} list below.")
    selection = inputs.prompt_from_choices(list(opts_dict.keys()))
    id_list.append(opts_dict[selection])

    return(filter_function(filter=column, id_list=id_list))

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
        model = data_model.CSVDataModel(kwargs["data_directory"])
        view_csv.main(db_select, mode, model)
    else:
        view_sql.main(db_select, mode, kwargs["sql_configs"])