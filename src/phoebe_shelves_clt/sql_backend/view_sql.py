from typing import Dict, Tuple
import psycopg2
import pandas as pd

from phoebe_shelves_clt.sql_backend import queries
from phoebe_shelves_clt.utils import sql_api
from phoebe_shelves_clt.utils import inputs

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
        query_function = queries.main_reading_query
    else:
        query_function = queries.main_books_query

    if threshold_mode == 1:
        lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[lower_thresh]))
    elif threshold_mode == 2:
        upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[upper_thresh]))
    elif threshold_mode == 3:
        lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[lower_thresh, upper_thresh]))
    else:  # threshold_mode == 4
        return(query_function(column, comp_type=threshold_mode, thresholds=[]))


def options_filter(conn, table: str, column: str) -> str:

    # Get correct options List
    if column == "Title":
        opts_dict = queries.retrieve_books_list(conn)
    else:
        opts_dict = queries.retrieve_authors_list(conn)

    # Select option
    id_list = []
    print(f"\nChoose from the {column.lower()} list below.")
    selection = inputs.prompt_from_choices(list(opts_dict.keys()))
    id_list.append(opts_dict[selection])

    # Generate the appropriate query
    if table == "books":
        return(queries.main_books_query(filter=column, id_list=id_list ))
    else:
        return(queries.main_reading_query(filter=column, id_list=id_list ))


def date_filter(conn, table: str, column: str):
    """Generates a date filter based on user input.

    Generates a SQL query that will filter the given table based on dates.

    TODO:
        * Complete this section
    """
    pass


def reading_filter(conn) -> str:
    """Filter the reading database based on user selection and inputs


    TODO:
        * Implement the date filter 
    """
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
    """ Filter the books database based on user selection and inputs

    TODO:
        * Implement method to filtering based on genre
    """
    opts = ["Title", "Author", "Times Read", "Rating", "Genre"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author"}:
        return(options_filter(conn, "books", selection))
    elif selection in {"Times Read", "Rating"}:
        return(numeric_filter("books", selection))
    else:  # Genre
        # TODO: Implement genre
        return("WIP")

def main(db_select: str, mode: str, sql_configs: Dict[str, str]):
    """ Main module function """

    conn = sql_api.connect_to_database(sql_configs["user"],
                                       sql_configs["database"])

    to_filter_prompt = "Would you like to filter/search the data first?"
    to_filter = inputs.confirm(to_filter_prompt)

    if db_select == "reading":
        query = reading_filter(conn) if to_filter else queries.main_reading_query()
    else:
        query = books_filter(conn) if to_filter else queries.main_books_query()

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

    conn.close()