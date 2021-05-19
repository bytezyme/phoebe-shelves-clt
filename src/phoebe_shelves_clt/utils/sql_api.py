#!usr/bin python
from typing import List, Tuple, Dict
import textwrap

import psycopg2
import sys
import pandas as pd

"""
### Notes
- Use pd.read_sql() to do all of the final selection and filtering queries
- Use psycopg2 for the actual insert and updates
"""

def connect_to_database(user: str, database: str):
    """ Connects to the PostgreSQL database

    Todo: 
        * Add support for more server configuration variables
        * Finish function documentation
    """
    
    try:
        conn = psycopg2.connect(user=user, database=database)
    except Exception as err:
        print(f"Cannot connect to the {database} database.")
        print(f"Error: {err}")
        sys.exit(1)
    else:
        print(f"Successfully connected to the {database} database.")
        return(conn)

def execute_query(conn, query: str, query_type: str):

    # Setup error message
    error_messages = {
        "create_db": "Could not create database. See below for details.",
        "create_table": "Could not create table. See below for details.",
        "drop_table": "Could not drop table. See below for details.",
        "to_list": "Query failed. See below for details.",
        "to_df": "Query failed. See below for details.",
        "modify": "Query failed. See below for details.",
        "modify_return": "Query failed. See below for details.",
        "basic": "Query failed. See below for details."
    }

    with conn.cursor() as cur:
        try:
            if query_type == "to_df":
                temp_df = pd.read_sql(query, conn)
            else:
                cur.execute(query)
        except Exception as err:
            print(error_messages[query_type])
            print(err)
            sys.exit(1)
        else:
            if query_type == "to_df":
                return(temp_df)  # type: ignore
            elif query_type in {"create_db", "create_table", "drop_table", "modify"}:
                conn.commit()
            elif query_type in {"modify_return"}:
                results = cur.fetchall()
                conn.commit()
                return(results)
            elif query_type == "to_list":
                return(cur.fetchall())
            else:
                pass

def create_database(conn, db_name):
    """ Create new database

    TODO:
        * Finish function documentation
    """
    query = f"create database {db_name}"
    execute_query(conn, query, "create_db")

# Table Management

def create_table(conn, query: str, table_name: str, force: bool):
    """ Create new table in database

    
    Todo:
        * Finish function documentation
    """

    if force:
        drop_table(conn, table_name)
    execute_query(conn, query, "create_table")

def drop_table(conn, table_name: str):
    """ Drops a table if it exists in the database
    """
    query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
    execute_query(conn, query, "drop_table")

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
    
    return(dict(execute_query(conn, query, "to_list")))  # type: ignore


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
    return(dict(execute_query(conn, query, "to_list"))) # type: ignore

def retrieve_genres_list(conn) -> Dict[str, int]:
    """ Retieve all genres in the genres table

    Retrieves all of the genres in the genres table and returns a dictionary
    mapping from the genre name to the genre ID

    Args:
        con (psycopg2.connection): Connection to the PostgreSQL database

    Returns:
        (dict): Dictionary mapping genre to the genre_id
    """

    query = textwrap.dedent("""\
                SELECT
                    name "Genre",
                    id "Genre ID"
                FROM genres
            """)
    return(dict(execute_query(conn, query, "to_list")))  # type: ignore

def query_books(filter: str = None, **kwargs) -> str:
    """ Generate SQL query for the books database
    """

    query = """
    create temp table books_friendly as (
        WITH 
            reading_agg (book_id, times_read, avg_rating) AS (
            SELECT
                book_id,
                COUNT(id) "times_read",
                AVG(rating)::NUMERIC(10,1) "avg_rating"
            FROM reading
            GROUP BY book_id
            ),

            books_authors_agg (book_id, authors) AS (
            SELECT
                ba.book_id,
                string_agg(a.first_name || COALESCE(' ' || a.middle_name, '') || ' ' || a.last_name, ', ')
            FROM books_authors ba
            INNER JOIN authors a
                on ba.author_id = a.id {}
            GROUP BY
                ba.book_id
            ),

            books_genres_agg (book_id, genres) AS (
            SELECT
                bg.book_id,
                string_agg(g.name, ', ')
            FROM books_genres bg
            INNER JOIN genres g
                on bg.genre_id = g.id
            GROUP BY
                bg.book_id
            )

        SELECT
            b.title "Title",
            ba.authors "Author(s)",
            b.book_length "Pages",
            COALESCE(r.times_read, 0) "Times Read",
            COALESCE(r.avg_rating, b.rating::Numeric(10,1)) "Rating",
            bg.genres "Genre"
        FROM books b
        INNER JOIN books_authors_agg ba
            on b.id = ba.book_id
        LEFT JOIN reading_agg r
            on b.id = r.book_id
        LEFT JOIN books_genres_agg bg
            on b.id = bg.book_id
        {}
    );
    select * from books_friendly;
    """

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

def query_reading(filter: str = None, **kwargs) -> str:
    query = """
    create temp table reading_friendly AS (
        WITH 
            books_authors_agg (book_id, authors) AS (
            SELECT
                ba.book_id,
                string_agg(a.first_name || COALESCE(' ' || a.middle_name, '') || ' ' || a.last_name, ', ')
            FROM books_authors ba
            INNER JOIN authors a
                on ba.author_id = a.id {}
            GROUP BY
                ba.book_id
        )
        SELECT
            r.id "ID",
            b.title "Title",
            ba.authors "Author(s)",
            r.start_date "Start",
            r.finish_date "Finish",
            r.rating "Rating",
            r.finish_date - r.start_date + 1 "Read Time"
        FROM reading r
        INNER JOIN books b
            on r.book_id = b.id
        INNER JOIN books_authors_agg ba
            on b.id = ba.book_id
        {}
        ORDER BY
            r.finish_date ASC NUllS Last
    );

    SELECT * from reading_friendly;
    """

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


def read_query(name: str):
    with open(f"src/phoebe_shelves_clt/utils/sql_queries/{name}.sql") as f:
        return(f.read())