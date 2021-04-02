"""Initializes empty databases in a given directory.

This module provides functions for creating empty databases in the provided
data directory.
"""

import os
import pandas as pd


def create_database(path, name, cols, db_exists, force_overwrite):
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

    if db_exists and not force_overwrite:
        print('{} database already created. Pass -f to force overwrite '
              'the current database.'.format(name.title()))
        create_db = False
    elif db_exists and force_overwrite:
        print('Overwriting existing {} database...'.format(name))
        create_db = True
    else:
        print('Creating the {} database...'.format(name))
        create_db = True

    if create_db:
        pd.DataFrame(columns=cols).to_csv(path, index=False)
        print('Successfully created the {} database!'.format(name))


def init_databases(force_overwrite, data_directory):
    """Creates initial book and reading date csv files if not present

    Args:
        force_overwrite {bool} -- Indicates to overwrite existing databases
        data_directory {string} -- Path to the data directory

    Returns:
        Prints out status of the process
        Writes empty reading and book databases to the data_directory
    """

    print('Checking for data...')
    books_path = data_directory + '/books.csv'
    reading_path = data_directory + '/reading.csv'

    # Books Database
    books_exists = os.path.isfile(books_path)
    books_cols = ['Title', 'Author', 'Author FN', 'Author MN',
                  'Author LN', 'Length', 'Times Read', 'Rating', 'Genre']
    create_database(books_path, 'books', books_cols,
                    books_exists, force_overwrite)

    # Reading Database
    reading_exists = os.path.isfile(reading_path)
    reading_cols = ['Title', 'Start', 'Finish', 'Reading Time', 'Rating']
    create_database(reading_path, 'reading', reading_cols,
                    reading_exists, force_overwrite)
