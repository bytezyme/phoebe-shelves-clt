""" Collection of common SQL queries and functions

Collection of common SQL query functions used throughout the SQL-based workflow
to retrieve information from the backend PostgreSQL database. Most queries are
stored and retrieved from separate SQL files within /sql_backend/sql_queries
"""

from typing import Dict

from phoebe_shelves_clt.utils import sql_api

def retrieve_authors_list(conn) -> Dict[str, int]:
    """ Retreive all authors in the authors table

    Retrieves all of the authors in the authors database and returns a dictionary
    mapping form the author name to the author id

    Args:
        conn (psycopg2.connection): Connection to PostgreSQL database
    
    Returns:
        (dict): Dictionary mapping author to author_id
    """

    # query = """
    # select
    #     a.first_name || COALESCE(' ' || a.middle_name, '') || ' ' || a.last_name "Author",
    #     id "Author ID"
    # from authors a
    # """
    query = sql_api.read_query("retrieve_authors_list")
    
    return(dict(sql_api.execute_query(conn, query, "to_list")))  # type: ignore


def retrieve_books_list(conn) -> Dict[str, int]:
    """ Retreive all books in the books table

    Retrieves all of the books in the books database and returns a dictionary
    mapping from the title to the book id

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database
    
    Returns:
        (dict): Dictionary mapping title to book_id
    """

    # query = """
    # select
    #     b.title "Title",
    #     id "Book ID"
    # from books b
    # """
    query = sql_api.read_query("retrieve_books_list")
    return(dict(sql_api.execute_query(conn, query, "to_list"))) # type: ignore


def retrieve_genres_list(conn) -> Dict[str, int]:
    """ Retieve all genres in the genres table

    Retrieves all of the genres in the genres table and returns a dictionary
    mapping from the genre name to the genre ID

    Args:
        con (psycopg2.connection): Connection to the PostgreSQL database

    Returns:
        (dict): Dictionary mapping genre to the genre_id
    """

    # query = textwrap.dedent("""\
    #             SELECT
    #                 name "Genre",
    #                 id "Genre ID"
    #             FROM genres
    #         """)
    query = sql_api.read_query("retrieve_genres_list")
    return(dict(sql_api.execute_query(conn, query, "to_list")))  # type: ignore


def main_books_query(filter: str = None, **kwargs) -> str:

    query = sql_api.read_query("main_books_query")
    if filter is None:
        return(query.format("",""))

    elif filter == "Title":
        id_list_string = ", ".join([str(id) for id in kwargs["id_list"]])
        return(query.format("", f"WHERE b.id in ({id_list_string})"))

    elif filter == "Author":
        id_list_string = ", ".join([str(id) for id in kwargs["id_list"]])
        return(query.format(f"and a.id in ({id_list_string})", ""))

    elif filter == "Times Read" or filter == "Rating":
        comp_type = kwargs["comp_type"]

        if filter == "Times Read":
            filter_string = "WHERE COALESCE(r.times_read, 0) "
        else:
            filter_string = ("WHERE COALESCE(r.avg_rating, "
                            "b.rating::Numeric(10,1)) ")

        if comp_type == 1:
            filter_string += "<= {}".format(kwargs["thresholds"][0])
        elif comp_type == 2:
            filter_string += ">= {}".format(kwargs["thresholds"][0])
        elif comp_type == 3:
            lower_threshold = kwargs["thresholds"][0]
            upper_threshold = kwargs["thresholds"][1]
            filter_string += "between {} and {}".format(lower_threshold,
                                                        upper_threshold)
        elif comp_type == 4:
            filter_string += "is null"
        return(query.format("", filter_string))
    else:  # Genre
        # TODO: Convert to using Genre table and mapping!
        genre_list_string = ",".join([f"'{genre}'" for genre in kwargs["genre_list"]])
        return(query.format("", f"WHERE b.genre in ({genre_list_string})"))


def main_reading_query(filter: str = None, **kwargs) -> str:
    query = sql_api.read_query("main_reading_query")
    if filter is None:
        return(query.format("", ""))
        
    elif filter == "Title":
        id_list_string = ", ".join([str(id) for id in kwargs["id_list"]])
        return(query.format("", f"WHERE b.id in ({id_list_string})"))

    elif filter == "Author":
        id_list_string = ", ".join([str(id) for id in kwargs["id_list"]])
        return(query.format(f"and a.id in ({id_list_string})", ""))

    elif filter == "Start" or filter == "Finish":
        comp_type = kwargs["comp_type"]
        
        if filter == "Start":
            filter_string = "WHERE r.start_date "
        else:
            filter_string = "WHERE r.end_date "

        if comp_type == 1:
            filter_string += "<= '{}'".format(kwargs["value"])
        elif comp_type == 2:
            filter_string += ">= '{}'".format(kwargs["value"])
        elif comp_type == 3:
            filter_string += "between '{}' and '{}'".format(kwargs["start"],
                                                        kwargs["stop"])
        elif comp_type == 4:
            # TODO: Need to figure out how to do proper conversion for years
            pass 
        elif comp_type == 5:
            filter_string += "is null"

        return(query.format("", filter_string))

    else:  # Reading Time or Rating
        comp_type = kwargs["comp_type"]

        if filter == "Reading Time":
            filter_string = "WHERE r.end_date - r.start_date + 1 "
        else:
            filter_string = "WHERE r.rating "

        if comp_type == 1:
            filter_string += "<= {}".format(kwargs["thresholds"][0])
        elif comp_type == 2:
            filter_string += ">= {}".format(kwargs["thresholds"][0])
        elif comp_type == 3:
            lower_threshold = kwargs["thresholds"][0]
            upper_threshold = kwargs["thresholds"][1]
            filter_string += "between {} and {}".format(lower_threshold,
                                                        upper_threshold)
        elif comp_type == 4:
            filter_string += "is null"

        return(query.format("", filter_string))