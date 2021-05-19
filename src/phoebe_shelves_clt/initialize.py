"""Methods for initializing databases.

This module provides functions for creating empty databases in the provided
data directory.
"""

import os
import pandas as pd
import textwrap

from .utils.inputs import confirm
from .utils import sql_api


def create_database(path, name, cols, force_overwrite):
    """ Checks and creates the database as needed

    Args:
        path {string} -- Path to database location
        name {string} -- Name of the database
        cols {list} -- List of column names
        force_overwrite {bool} -- Indicator to save new database if one exists

    Returns:
        Saves an empty database with appropriate column names to path
    """

    db_exists = os.path.isfile(path)

    if db_exists and not force_overwrite:
        prompt = (f'The {name} database already exists. Would you like to '
                  'overwrite the existing database?')
        create_db = confirm(prompt)
    else:
        create_db = True

    if create_db:
        pd.DataFrame(columns=cols).to_csv(path, index=False)
        print(f'Successfully created the {name} database!')


def init_module(force_overwrite, data_directory):
    """Creates initial book and reading date csv files if not present

    Args:
        force_overwrite {bool} -- Indicates to overwrite existing databases
        data_directory {string} -- Path to the data directory

    Returns:
        Writes empty reading and book databases to the data_directory
    """

    books_path = data_directory + '/books.csv'
    reading_path = data_directory + '/reading.csv'

    # Books Database
    books_cols = ['Title', 'Author', 'Author FN', 'Author MN',
                  'Author LN', 'Length', 'Times Read', 'Rating', 'Genre']
    create_database(books_path, 'books', books_cols, force_overwrite)

    # Reading Database
    reading_cols = ['Title', 'Start', 'Finish', 'Reading Time', 'Rating']
    create_database(reading_path, 'reading', reading_cols, force_overwrite)


#-------------- SQL Implementations -------------------#

def init_sql(force_overwrite, sql_configs):
    conn = sql_api.connect_to_database(sql_configs["user"],
                                       sql_configs["database"])

    # Create primary tables
    init_table(conn, force_overwrite, "books")
    init_table(conn, force_overwrite, "authors")
    init_table(conn, force_overwrite, "series")
    init_table(conn, force_overwrite, "genres")
    init_table(conn, force_overwrite, "reading")

    # # Create relationship tables
    init_table(conn, force_overwrite, "books_authors")
    init_table(conn, force_overwrite, "books_genres")
    init_table(conn, force_overwrite, "books_series")

def init_table(conn, force_overwrite, table_name):
    table_queries = {
        "authors": textwrap.dedent("""\
                    CREATE TABLE authors (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        first_name TEXT,
                        middle_name TEXT,
                        last_name TEXT,
                        suffix TEXT,
                        UNIQUE(first_name, middle_name, last_name, suffix)
                    );
                    """),
        "books": textwrap.dedent("""\
                    CREATE TABLE books (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        title TEXT,
                        book_length INT,
                        rating INT,
                        UNIQUE(id, title)
                    );
                    """),
        "genres": textwrap.dedent("""\
                    CREATE TABLE genres (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        name TEXT,
                        UNIQUE(name)
                    );
                    """),
        "reading": textwrap.dedent("""\
                    CREATE TABLE reading (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        book_id INT REFERENCES books(id) ON DELETE CASCADE,
                        start_date DATE,
                        finish_date DATE,
                        rating INT,
                        UNIQUE(id, book_id, start_date, finish_date)
                    );
                    """),
        "series": textwrap.dedent("""\
                    CREATE TABLE series (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        series_name TEXT,
                        UNIQUE(series_name)
                    );
                    """),
        "books_authors": textwrap.dedent("""\
                            CREATE TABLE books_authors (
                                book_id INT REFERENCES books(id) ON DELETE CASCADE,
                                author_id INT REFERENCES authors(id) ON DELETE CASCADE,
                                PRIMARY KEY (author_id, book_id),
                                UNIQUE(author_id, book_id)
                            );
                            """),
        "books_genres": textwrap.dedent("""\
                            CREATE TABLE books_genres (
                                book_id INT REFERENCES books(id) ON DELETE CASCADE,
                                genre_id INT REFERENCES genres(id) ON DELETE CASCADE,
                                UNIQUE(book_id, genre_id)
                            );
                            """),
        "books_series": textwrap.dedent("""\
                            CREATE TABLE books_series (
                                book_id INT REFERENCES books(id) ON DELETE CASCADE,
                                series_id INT REFERENCES series(id) ON DELETE CASCADE,
                                series_order INT,
                                UNIQUE(book_id, series_id, series_order)
                            );
                            """)
    }
    sql_api.create_table(conn, table_queries[table_name],
                         table_name, force_overwrite)