"""Methods for initializing databases.

This module provides functions for creating empty databases in the provided
data directory.
"""

import os
import pandas as pd
from ..utils.inputs import confirm


def create_database(path, name, cols, force_overwrite):
    """ Checks and creates the database as needed

    Args:
        path {string} -- Path to database save location
        name {string} -- Name of the database
        cols {list} -- List of column names
        db_exists {bool} -- True if database exists at path
        force_overwrite {bool} -- Indicator to save new database if one exists

    Returns:
        Saves an empty database with appropriate column names to path
    """

    db_exists = os.path.isfile(path)

    if db_exists and not force_overwrite:
        prompt = ('The {} database already exists. Would you like to '
                  'overwrite the existing database?'.format(name))
        create_db = confirm(prompt)
    else:
        create_db = True

    if create_db:
        pd.DataFrame(columns=cols).to_csv(path, index=False)
        print('Successfully created the {} database!'.format(name))


def init_module(force_overwrite, data_directory):
    """Creates initial book and reading date csv files if not present

    Args:
        force_overwrite {bool} -- Indicates to overwrite existing databases
        data_directory {string} -- Path to the data directory

    Returns:
        Prints out status of the process
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
