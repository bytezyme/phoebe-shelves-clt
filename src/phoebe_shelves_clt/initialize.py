""" Methods for initializing backend databases.

Provides functions and workflow for preparing the backend databases for the
command-line tools.
"""

import os
from typing import List

import pandas as pd

from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.utils import sql_api


def create_database(path: str, name: str, cols: List[str],
                    force_overwrite: bool):
    """ Checks and creates the database as needed

    Creates the CSV database with the correct columns at the specified
    file location.

    Args:
        path: Path to database location.
        name: Name of the database.
        cols: List of column names.
        force_overwrite: Indicator to save new database if one exists.
    """
    db_exists = os.path.isfile(path)

    if db_exists and not force_overwrite:
        prompt = (f"The {name} database already exists. Would you like to "
                  "overwrite the existing database?")
        create_db = inputs.confirm(prompt)
    else:
        create_db = True

    if create_db:
        pd.DataFrame(columns=cols).to_csv(path, index=False)
        print(f"Successfully created the {name} database!")


def create_table(conn, force_overwrite: bool, table_name: str):
    """ Creates the indicated table in the backend SQL database

    Retrieves the appropriate creation query from utiles.sql_queries and
    executes the query to create the table in the SQL database

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database
        force_overwrite: Indicates whether to overwrite an existing table with
            the fresh table.
        table_name: Name of the table to create
    """
    query = sql_api.read_query(f"create_{table_name}_table")
    sql_api.create_table(conn, query, table_name, force_overwrite)


def init_module(backend: str, force_overwrite: bool, **kwargs):
    """ Creates initial book and reading date csv files if not present

    Parent function for begining the initialization of the backend databases.
    This function will call the appropriate initialization workflow depending
    on the selected backend.

    Args:
        backend: Indicates whether to use the CSV or SQL backend workflows
        force_overwrite: Indicates to overwrite existing databases

    Keyword Args:
        data_directory (str): Directory to store CSV backend files
        sql_configs (Dict): SQL database configurations
    """
    if backend == "csv":
        data_directory = kwargs["data_directory"]
        books_path = data_directory + "/backend/books.csv"
        reading_path = data_directory + "/backend/reading.csv"
        authors_path = data_directory + "/backend/authors.csv"
        genres_path = data_directory + "/backend/genres.csv"
        series_path = data_directory + "/backend/series.csv"
        books_authors_path = data_directory + "/backend/books_authors.csv"
        books_genres_path = data_directory + "/backend/books_genres.csv"
        books_series_path = data_directory + "/backend/books_series.csv"

        books_cols = ["id", "title", "book_length", "rating"]
        create_database(books_path, 'books', books_cols, force_overwrite)

        reading_cols = ["id", "book_id", "start_date", "finish_date", "rating"]
        create_database(reading_path, "reading", reading_cols, force_overwrite)

        authors_cols = ["id", "first_name", "middle_name", "last_name", "suffix"]
        create_database(authors_path, "authors", authors_cols, force_overwrite)

        genres_cols = ["id", "name"]
        create_database(genres_path, "genres", genres_cols, force_overwrite)

        series_cols = ["id", "name"]
        create_database(series_path, "series", series_cols, force_overwrite)

        books_authors_cols = ["book_id", "author_id"]
        create_database(books_authors_path, "books_authors",
                        books_authors_cols, force_overwrite)

        books_genres_cols = ["book_id", "genre_id"]
        create_database(books_genres_path, "books_genres",
                        books_genres_cols, force_overwrite)

        books_series_cols = ["book_id", "series_id"]
        create_database(books_series_path, "books_series",
                        books_series_cols, force_overwrite)

    else:
        sql_configs = kwargs["sql_configs"]
        conn = sql_api.connect_to_database(sql_configs["user"],
                                           sql_configs["database"])

        # Basic tables
        create_table(conn, force_overwrite, "books")
        create_table(conn, force_overwrite, "authors")
        create_table(conn, force_overwrite, "series")
        create_table(conn, force_overwrite, "genres")
        create_table(conn, force_overwrite, "reading")

        # Relationship tables
        create_table(conn, force_overwrite, "books_authors")
        create_table(conn, force_overwrite, "books_genres")
        create_table(conn, force_overwrite, "books_series")