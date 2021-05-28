""" Visualization of the database using the SQL backend

Visualize the backend database with options to filter, aggregate,
and transform the data into other formats using the SQL backend.

Todo:
    * Implement chart-based visualization using graphing modules
    * Implement aggregate statistics characterizations. 
"""

from typing import Dict

from phoebe_shelves_clt.sql_backend import queries
from phoebe_shelves_clt.utils import sql_api
from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt import view

def print_table(conn, query: str):
    """ Prints SQL query result as formatted table

    Prints the result of a SQL query as a formatted table via the 
    pandas.DataFrame.to_markdown() method
    
    Args:
        conn (psycopg2.connection): Connection to PostgreSQL database
        query: SQL query to execute
    """
    results = sql_api.execute_query(conn, query, "to_df")
    print(results.to_markdown(tablefmt='grid', index=False))


## --------------- Basic Filters --------------- ##


def reading_filter(conn) -> str:
    """ Generate reading filter based on user inputs.

    Generates an appropriate SQL query to filter the reading database based on
    user inputs.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.

    Returns:
        SQL query with the appropriate filter.
    """
    opts = ["Title", "Author", "Start", "Finish", "Reading Time", "Rating"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author"}:
        return(view.options_filter("reading", selection, "sql",
                                   conn=conn)) # type: ignore
    elif selection in {"Start", "Finish"}:
        return(view.date_filter("reading", selection, "sql"))  # type: ignore
    else:  # Reading Time and Rating
        return(view.numeric_filter("books", selection, "sql"))  # type: ignore


def books_filter(conn) -> str:
    """ Filter the books database based on user selection and inputs

    Generates an appropriate SQL query to filter the books database based on
    user inputs.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.

    Returns:
        SQL query with the appropriate filter.

    """
    opts = ["Title", "Author", "Times Read", "Rating", "Genre"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author", "Genre"}:
        return(view.options_filter("reading", selection, "sql",
                                   conn=conn)) # type: ignore
    else: # "Times Read", "Rating"
        return(view.numeric_filter("books", selection, "sql"))  # type: ignore

def main(db_select: str, mode: str, sql_configs: Dict[str, str]):
    """ Main module function
    
    Main view module function to launch different workflows to visualize the
    different databases. Databases are first merged into a user-friendly
    presentation.
    
    Args:
        db_select: Which database to visualze.
        mode: Which visualization mode to utilize
        sql_configs: Configurations for the PostgreSQL database

    Todo:
        * Implement chart visualization
        * Implement aggregate statistics
    """

    conn = sql_api.connect_to_database(sql_configs["user"],
                                       sql_configs["database"])

    to_filter_prompt = "Would you like to filter/search the data first?"
    to_filter = inputs.confirm(to_filter_prompt)

    if db_select == "reading" and to_filter:
        query = reading_filter(conn)
    elif db_select == "reading" and not to_filter:
        query = queries.main_reading_query()
    elif db_select == "books" and to_filter:
        query = books_filter(conn)
    else:
        query = queries.main_books_query()

    if mode == "table":
        print_table(conn, query)
    elif mode == "chart":
        # TODO: Implement chart visualization
        # ? TEMP TABLE: books_friendly/reading_friendly
        print("Chart visualization is not currently implemented.")
    elif mode == "stats":
        # TODO: Implement aggregate statistics
        # ? TEMP TABLE: books_friendly/reading_friendly
        print("Chart visualization is not currently implemented.")

    conn.close()