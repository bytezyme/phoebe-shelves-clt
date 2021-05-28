""" Launching point and supporting functions for database management tools.

This module serves as the launching point for the database management tools.
Backend-specific implementations are located within their specific modules and
common functions and methods are included in this file.
"""

import numpy as np

from typing import Tuple, Dict

from phoebe_shelves_clt.csv_backend import manage_csv
from phoebe_shelves_clt.sql_backend import manage_sql
from phoebe_shelves_clt.utils import data_model
from phoebe_shelves_clt.utils import sql_api

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

def prompt_for_title(backend: str, *args) -> Tuple[str, Dict[str, int]]:
    """ Prompt for a title from the books table and return the title and ID

    Prompts the user to provide a title and returns the title and ID of any
    books that match the title *exactly*.

    Args:
        backend: Backend to use
    
    Positional Args:
        (CSVDataModel): Current instance of the CSV backend database
        (psycopg2.connection): Connection to the PostgreSQL database
    
    Returns:
        A tuple containing the following:
            title: Title of the book provided by the user
            title_results: Dictionary mapping possible titles to their ID's
    """
    title = input("Please enter the book title: ")

    if backend == "csv":
        title_results = args[0].get_books_dict(title)
    else:
        query = f"SELECT title, id FROM books WHERE title ILIKE '{title}'"
        title_results = dict(sql_api.execute_query(args[0], query,
                                                   "to_list"))  # type: ignore

    return(title, title_results)

def prompt_for_author(backend: str, *args) -> Tuple[str, Dict]:
    """ Prompt for an author from the authors table and return the name and ID

    Prompts the user to provide an author's last name and returns the names
    and ID's of possible matches based on the last name.

    Args:
        backend: Backend to use
    
    Positional Args:
        (CSVDataModel): Current instance of the CSV backend database
        (psycopg2.connection): Connection to the PostgreSQL database
    
    Returns:
        A tuple containing the following:
            last_name: Last name provided by the user
            author_results: Dictionary mapping possible authors to their ID's
    """
    last_name = input("Please enter the author's last name: ")

    if backend == "csv":
        author_results = args[0].get_authors_dict(last_name)
    else:
        author_query = (sql_api.read_query('author_filter').format(last_name))
        author_results = dict(sql_api.execute_query(args[0], author_query,
                                                    "to_list"))  # type: ignore
    return(last_name, author_results)

def prompt_for_genre(backend: str, *args) -> Tuple[str, Dict]:
    """ Prompt for an genre from the genres table and return the name and ID

    Prompts user to enter a genre name. It then retrieves the potential
    matching options for further processing.

    Args:
        backend: Backend to use
    
    Positional Args:
        (CSVDataModel): Current instance of the CSV backend database
        (psycopg2.connection): Connection to the PostgreSQL database
    
    Returns:
        A tuple containing the following:
            genre_name: Genre name provided by the user
            genreresults: Dictionary mapping possible genres to their ID's
    """
    genre_name = input("Please enter the genre name: ")

    if backend == "csv":
        genre_results = args[0].get_genres_dict(genre_name)
    else:
        genre_query = f"SELECT name, id from genres where name ilike '{genre_name}'"
        genre_results = dict(sql_api.execute_query(args[0], genre_query,
                                                   "to_list"))  # type: ignore
    return(genre_name, genre_results)

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