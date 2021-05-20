""" Collection of common SQL queries and functions

Collection of common SQL query functions used throughout the SQL-based workflow
to retrieve information from the backend PostgreSQL database. Most queries are
stored and retrieved from separate SQL files within /sql_backend/sql_queries
"""

from typing import Dict, List

from phoebe_shelves_clt.utils import sql_api

def retrieve_authors_list(conn) -> Dict[str, int]:
    """ Retreive all authors in the authors table

    Retrieves all of the authors in the authors database and returns a
    dictionary mapping form the author name to the author id

    Args:
        conn (psycopg2.connection): Connection to PostgreSQL database
    
    Returns:
        Dictionary mapping author to author_id
    """
    query = sql_api.read_query("retrieve_authors_list")
    return(dict(sql_api.execute_query(conn, query, "to_list")))  # type: ignore


def retrieve_books_list(conn) -> Dict[str, int]:
    """ Retreive all books in the books table

    Retrieves all of the books in the books database and returns a dictionary
    mapping from the title to the book id

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database
    
    Returns:
        Dictionary mapping title to book_id
    """
    query = sql_api.read_query("retrieve_books_list")
    return(dict(sql_api.execute_query(conn, query, "to_list"))) # type: ignore


def retrieve_genres_list(conn) -> Dict[str, int]:
    """ Retieve all genres in the genres table

    Retrieves all of the genres in the genres table and returns a dictionary
    mapping from the genre name to the genre ID

    Args:
        con (psycopg2.connection): Connection to the PostgreSQL database

    Returns:
        Dictionary mapping genre to the genre_id
    """
    query = sql_api.read_query("retrieve_genres_list")
    return(dict(sql_api.execute_query(conn, query, "to_list")))  # type: ignore


def numeric_filter_string(filter_string: str, comp_type: int,
                          thresholds: List[int]) -> str:
    """ Generate string for a numeric filter.

    Generates a numeric filter string that will be added to the main
    SQL query.

    Args:
        filter_string: Start of the filter string containing the column
        comp_type: Indicates a [1] ≤ comparison, [2] ≥ comparison, [3] range,
            or [4] missing value filter
        thresholds: List of threshold values for the comparisons
    
    Returns:
        filter_string: The formatted numeric filter string
    """
    if comp_type == 1:
        filter_string += "<= {}".format(thresholds[0])
    elif comp_type == 2:
        filter_string += ">= {}".format(thresholds[0])
    elif comp_type == 3:
        filter_string += f"between {thresholds[0]} and {thresholds[1]}"
    elif comp_type == 4:
        filter_string += "is null"
    return(filter_string)


def opt_filter_string(filter_string: str, id_list: List[int]):
    """ Generate string for option-based filter.

    Generates a filter for filtering for specific rows based on the unique
    element ID that will be added to the main SQL query.

    Args:
        filter_string: Start of the filter string containing the column.
        id_list: List of element ID that will be filtered for.
    
    Returns:
        filter_string: The formatted options filter string.
    """
    id_list_string = ", ".join([str(element_id) for element_id in id_list])
    return(filter_string + f"({id_list_string})")


def date_filter_string(column: str, comp_type: int,
                      thresholds: List[str]):
    """ Generate string for date-based filters

    Generates a filter for filtering for specific rows based on different
    date comparisons.

    Args:
        column: Column to filter on
        comp_type: Indicates a [1] earliest date, [2] latest date, [3] range
            of dates, [4] specific year, and [5] missing date values.
        thresholds: List of threshold values for the filter
    
    Returns:
        filter_string: The formatted options filter string.
    """
    if comp_type == 1:
        filter_string = f"WHERE {column} >= '{thresholds[0]}'"

    elif comp_type == 2:
        filter_string = f"WEHERE {column} <= '{thresholds[0]}'"

    elif comp_type == 3:
        filter_string = "WHERE {} between '{}' and '{}'".format(column,
                                                                thresholds[0],
                                                                thresholds[1])

    elif comp_type == 4:
        filter_string = f"WHERE EXTRACT (YEAR FROM {column}) = {thresholds[0]}"

    else:
        filter_string = f"WHERE {column} is null"

    return(filter_string)

def main_books_query(filter: str = None, **kwargs) -> str:
    """ Generate the main books query

    Generates the main query for create a temporary user-friendly books table,
    primarily used for printing to the command-line. This query supports a
    variety of filtering options to clean up the final output.

    Args:
        filter: Indicates what filter to utilize
    
    Keyword Args:
        id_list (List[int]): List of unique ID's for selection filters
        comp_type (str): Indicates the comparison type for numeric filters
        thresholds (List[int]): Threshold values for numeric filters
        genre_list (List[str]): List of genres for the genre filter

    Returns:
        A string-representation of the final query with additional filters.
    """
    query = sql_api.read_query("main_books_query")

    if filter is None:
        return(query.format("","", ""))

    elif filter == "Title":
        filter_string = opt_filter_string("WHERE b.id in ", kwargs["id_list"])
        return(query.format("", "", filter_string))

    elif filter == "Author":
        filter_string = opt_filter_string("AND a.id in ", kwargs["id_list"])
        return(query.format(filter_string, "", ""))

    elif filter == "Times Read":
        filter_start = "WHERE COALESCE(r.times_read, 0) "
        filter_string = numeric_filter_string(filter_start, kwargs["comp_type"],
                                              kwargs["thresholds"])
        return(query.format("", "", filter_string))

    elif filter == "Rating":
        filter_start = "WHERE COALESCE(r.avg_rating, b.rating::Numeric(10,1)) "
        filter_string = numeric_filter_string(filter_start, kwargs["comp_type"],
                                              kwargs["thresholds"])
        return(query.format("", "", filter_string))

    else:  # Genre
        filter_string = opt_filter_string("WHERE g.id in ", kwargs["id_list"])
        return(query.format("", filter_string, ""))


def main_reading_query(filter: str = None, **kwargs) -> str:
    """ Generate main query for user-friendly reading database representation

    Generates the appropriate SQL query (with filters, as necessary) to create
    the user-friendly representation of the reading database.

    Args:
        filter: Which filter should be implemented

    Keyword Arguments:
        id_list (List[int]): List of unique ID's for selection filters
        comp_type (str): Indicates the comparison type for numeric filters
        thresholds (List[int]): Threshold values for numeric filters
        genre_list (List[str]): List of genres for the genre filter  
    """
    query = sql_api.read_query("main_reading_query")

    if filter is None:
        return(query.format("", ""))
        
    elif filter == "Title":
        filter_string = opt_filter_string("WHERE b.id in ", kwargs["id_list"])
        return(query.format("", filter_string))

    elif filter == "Author":
        filter_string = opt_filter_string("AND a.id in ", kwargs["id_list"])
        return(query.format(filter_string, ""))

    elif filter == "Start":
        filter_string = date_filter_string("r.start_date ",
                                           kwargs["comp_type"],
                                           kwargs["thresholds"])
        return(query.format("", filter_string))
    elif filter == "Finish":
        filter_string = date_filter_string("r.finish_date ",
                                           kwargs["comp_type"],
                                           kwargs["thresholds"])
        return(query.format("", filter_string))       
    elif filter == "Reading Time":
        filter_start = "WHERE r.finish_date - r.start_date + 1 "
        filter_string = numeric_filter_string(filter_start,
                                              kwargs["comp_type"],
                                              kwargs["thresholds"])
        return(query.format("", filter_string))
    else:  # Rating
        filter_string = numeric_filter_string("WHERE r.rating ",
                                              kwargs["comp_type"],
                                              kwargs["thresholds"])
        return(query.format("", filter_string))