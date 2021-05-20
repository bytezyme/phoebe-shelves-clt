""" Visualization of books data

Visualize data about the books database. This module utilizes the aggregated
books database for a more user-friendly format.
"""

from typing import Dict

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
    """
    results = sql_api.execute_query(conn, query, "to_df")
    print(results.to_markdown(tablefmt='grid', index=False))


## --------------- Basic Filters --------------- ##

def numeric_filter(table: str, column: str) -> str:
    """ Generate a numeric filter based on user input

    Generates the correct SQL filter using numeric thresholds provided by the
    user via interactive command-line prompts.

    Args:
        table: Name of the table being used
        column: Column to filter on
    
    Returns:
        SQL query with appropriate filters
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


def date_filter(table: str, column: str) -> str:
    """ Generates a date filter based on user input.

    Generates a SQL query that will filter the given table based on dates.

    Args:
        table: Name of the table being used
        column: Column to filter on
    
    Returns:
        SQL query with appropriate filters
    """
    threshold_prompt = ("Would you like to filter based on an [1] earliest date "
                        "(anytime after), [2] latest date (anytime before), "
                        "[3] range of dates, [4] specific year, or [5] "
                        "missing dates?: ")
    threshold_mode = inputs.prompt_from_choices([1,2,3,4,5], threshold_prompt)
    early_date_prompt = "What's the earliest date (inclusive)?: "
    late_date_prompt = "What's the latest date (inclusive)?: "
    year_prompt = "What year would you like to view?: "

    if table == "reading":
        query_function = queries.main_reading_query
    else:
        query_function = queries.main_books_query

    if threshold_mode == 1:
        early_date = inputs.prompt_for_date(early_date_prompt, as_string=True)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[early_date]))
    elif threshold_mode == 2:
        late_date = inputs.prompt_for_date(late_date_prompt, as_string=True)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[late_date]))
    elif threshold_mode == 3:
        early_date = inputs.prompt_for_date(early_date_prompt, as_string=True)
        late_date = inputs.prompt_for_date(late_date_prompt, as_string=True)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[early_date, late_date]))
    elif threshold_mode == 4:
        year = inputs.prompt_for_date(year_prompt, as_string=True)
        return(query_function(column, comp_type=threshold_mode,
                              thresholds=[year]))

    else:
        return(query_function(column, comp_type=threshold_mode, thresholds=[]))

def options_filter(conn, table: str, column: str) -> str:
    """ Filter based on a set of options

    Filter the data based on a finite number of options.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database
        table: Name of the table to filter
        column: Name of the column to filter on

    Returns:
        SQL query with the appropriate filters
    """

    # Get correct options List
    if column == "Title":
        opts_dict = queries.retrieve_books_list(conn)
    elif column == "Author":
        opts_dict = queries.retrieve_authors_list(conn)
    else:
        opts_dict = queries.retrieve_genres_list(conn)

    # Select option
    id_list = []
    print(f"\nChoose from the {column.lower()} list below.")
    selection = inputs.prompt_from_choices(list(opts_dict.keys()))
    id_list.append(opts_dict[selection])

    # Generate the appropriate query
    if table == "books":
        return(queries.main_books_query(filter=column, id_list=id_list))
    else:
        return(queries.main_reading_query(filter=column, id_list=id_list))


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
        return(options_filter(conn, "reading", selection))
    elif selection in {"Start", "Finish"}:
        return(date_filter("reading", selection))
    else:  # Reading Time and Rating
        return(numeric_filter("reading", selection))


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
        return(options_filter(conn, "books", selection))
    else: # "Times Read", "Rating"
        return(numeric_filter("books", selection))

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