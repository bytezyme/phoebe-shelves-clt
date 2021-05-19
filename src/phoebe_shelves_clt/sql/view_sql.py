from typing import Dict, Tuple
import psycopg2
import pandas as pd
import sys

from ..utils import sql_api
from ..utils import inputs

def print_table(conn, query: str):
    """ Prints SQL query result as formatted table

    Prints the result of a SQL query as a formatted table via the 
    pandas.DataFrame.to_markdown() method
    
    Args:
        conn (psycopg2.connection): Connection to PostgreSQL database
        query: SQL query to execute

    Returns:
        Prints result as formatted table to command line

    """
    results = sql_api.execute_query(conn, query, "to_df")
    print(results.to_markdown(tablefmt='grid', index=False))

def retrieve_authors_list(conn) -> Dict[str, int]:
    """ Retreive all authors in the authors table

    Retrieves all of the authors in the authors database and returns a dictionary
    mapping form the author name to the author id

    Args:
        conn (psycopg2.connection): Connection to PostgreSQL database
    
    Returns:
        (dict): Dictionary mapping author to author_id
    """

    query = """
    select
        a.first_name || COALESCE(' ' || a.middle_name, '') || ' ' || a.last_name "Author",
        id "Author ID"
    from authors a
    """
    
    return(dict(sql_api.execute_query(conn, query, "to_list")))  #type: ignore

def retrieve_books_list(conn) -> Dict[str, int]:
    """ Retreive all books in the books table

    Retrieves all of the books in the books database and returns a dictionary
    mapping from the title to the book id

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database
    
    Returns:
        (dict): Dictionary mapping title to book_id
    """

    query = """
    select
        b.title "Title",
        id "Book ID"
    from books b
    """
    return(dict(sql_api.execute_query(conn, query, "to_list")))  #type: ignore

def retrieve_genre_list(conn) -> Dict[str, int]:
    """ Retrieve a list of genres in the genre table

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database

    Returns:
        (dict): Dictionary mapping genre to genre_id
    """

    query = """
    select
        name "Genre",
        id "Genre ID",
    from genre
    """
    return(dict(sql_api.execute_query(conn, query, "to_list")))  #type: ignore

def retrieve_columns(conn, table_name: str) -> Tuple[str]:
    """ Retrieve the columns of a table in the database

    Retrieves the column names of a given table in the currently-connected
    database.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database
        table_name: Name of the table to work with
    
    Returns:
        (Tuple[str]): Tuple of column names as strings

    """
    query = ("select column_name from information_schema.columns where "
              "table_name = '{}';".format(table_name))

    result = sql_api.execute_query(conn, query, "to_list")
    return(list(zip(*result))[0])


## General Filters

def numeric_filter(table: str, column: str) -> str:
    """Generate a numeric filter based on user input

    Generates the correct SQL filter using numeric thresholds provided by the
    user via interactive command-line prompts.

    Args:
        table {str} -- Name of the table being used
        column {str} -- Column to filter on
    
    Outputs:
        {str} -- SQL query with appropriate filters
    """

    threshold_prompt = ("Would you like to filter based on a [1] ≤ threshold, "
                        "[2] ≥ threshold, [3] range, or [4] missing values?: ")
    threshold_mode = inputs.prompt_from_choices([1,2,3,4], threshold_prompt)
    lower_thresh_prompt = "What's the smallest value (inclusive)?: "
    upper_thresh_prompt = "What's the largest_value (inclusive)?: "

    if table == "reading":
        query_function = sql_api.query_reading
    else:
        query_function = sql_api.query_books

    if threshold_mode == 1:
        _, lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[lower_thresh]))
    elif threshold_mode == 2:
        _, upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[upper_thresh]))
    elif threshold_mode == 3:
        _, lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        _, upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[lower_thresh, upper_thresh]))
    else:  # threshold_mode == 4
        return(query_function(column, comp_type=threshold_mode, thresholds=[]))


def options_filter(conn, table: str, column: str) -> str:

    # Get correct options List
    if column == "Title":
        opts_dict = retrieve_books_list(conn)
    else:
        opts_dict = retrieve_authors_list(conn)

    # Select option
    id_list = []
    print(f"\nChoose from the {column.lower()} list below.")
    selection = inputs.prompt_from_choices(list(opts_dict.keys()))
    id_list.append(opts_dict[selection])

    # Generate the appropriate query
    if table == "books":
        return(sql_api.query_books(filter=column, id_list=id_list ))
    else:
        return(sql_api.query_reading(filter=column, id_list=id_list ))

def date_filter(conn, table: str, column: str):
    pass

def reading_filter(conn) -> str:
    opts = ["Title", "Author", "Start", "Finish", "Reading Time", "Rating"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author"}:
        return(options_filter(conn, "reading", selection))
    elif selection in {"Start", "Finish"}:
        # TODO: Implement date filter!
        return("WIP")
    else:  # Reading Time and Rating
        return(numeric_filter("reading", selection))


def books_filter(conn) -> str:
    opts = ["Title", "Author", "Times Read", "Rating", "Genre"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author"}:
        return(options_filter(conn, "books", selection))
    elif selection in {"Times Read", "Rating"}:
        return(numeric_filter("books", selection))
    else:  # Genre
        # TODO: Implement genre
        return("WIP")

def view_sql(db_select: str, mode: str, sql_configs: Dict[str, str]):
    """ Main module function """
    # Connect to database
    conn = sql_api.connect_to_database(sql_configs["user"],
                                       sql_configs["database"])

    to_filter_prompt = "Would you like to filter/search the data first?"
    to_filter = inputs.confirm(to_filter_prompt)

    if db_select == "reading":
        query = reading_filter(conn) if to_filter else sql_api.query_reading()
    else:
        query = books_filter(conn) if to_filter else sql_api.query_books()

    if mode == "table":
        print_table(conn, query)
    elif mode == "chart":
        # TODO: NEED TO IMPLEMENT
        # ? TEMP TABLE: books_friendly/reading_friendly
        pass
    elif mode == "stats":
        # TODO: NEED TO IMPLEMENT
        # ? TEMP TABLE: books_friendly/reading_friendly
        pass

    # ! Make sure to close database
    conn.close()