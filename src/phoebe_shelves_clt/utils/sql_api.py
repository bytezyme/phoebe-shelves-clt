#!usr/bin python
from typing import List, Tuple

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


def create_database(conn, db_name):
    """ Create new database

    TODO:
        * Finish function documentation
    """
    query = f"create database {db_name}"
    
    with conn.cursor() as cur:
        try:
            cur.execute(query)
        except Exception as err:
            print("Creation failed. See below for exception.")
            print(err.pgcode)
            sys.exit(1)
        else:
            conn.commit()


def create_table(conn, query: str):
    """ Create new table in database

    
    Todo:
        * Finish function documentation
    """
    with conn.cursor() as cur:
        try:
            cur.execute(query)
        except Exception as err:
            print(err)
            sys.exit(1)
        else:
            conn.commit()

def drop_table(conn, table_name: str):
    """ Drops a table if it exists in the database
    """

    with conn.cursor() as cur:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        except Exception as err:
            print(err)
            sys.exit(1)
        else:
            conn.commit()

# Modify Tables

# Query Tables

def query_to_list(conn, query) -> List:
    """ Run query and return all rows as Python list

    Todo:
        * Finish function documentation
    """

    with conn.cursor() as cur:
        try:
            cur.execute(query)
        except Exception as err:
            print("Query failed. See below for exception.")
            print(err.pgcode)
            sys.exit(1)
        else:
            return(cur.fetchall())


def query_to_df(sql_query, conn) -> pd.DataFrame:
    """ Runs a query and returns output as a DataFrame
    """

    try:
        temp_df = pd.read_sql(sql_query, conn)
    except Exception as err:
        print("Query failed. See below for exception")
        print(err)
        sys.exit(1)
    else:
        return(temp_df)


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
        book_author_agg (book_id, authors) AS (
        SELECT
            ba.book_id,
            string_agg(a.first_name || COALESCE(' ' || a.middle_name, '') || ' ' || a.last_name, ', ')
        FROM book_author ba
        INNER JOIN authors a
            on ba.author_id = a.id {}
        GROUP BY
            ba.book_id
        )
        SELECT
            b.title "Title",
            ba.authors "Author(s)",
            b.book_length "Pages",
            COALESCE(r.times_read, 0) "Times Read",
            COALESCE(r.avg_rating, b.rating::Numeric(10,1)) "Rating",
            b.genre "Genre"
        FROM books b
        INNER JOIN book_author_agg ba
            on b.id = ba.book_id
        LEFT JOIN reading_agg r
            on b.id = r.book_id
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
            book_author_agg (book_id, authors) AS (
            SELECT
                ba.book_id,
                string_agg(a.first_name || COALESCE(' ' || a.middle_name, '') || ' ' || a.last_name, ', ')
            FROM book_author ba
            INNER JOIN authors a
                on ba.author_id = a.id {}
            GROUP BY
                ba.book_id
        )
        SELECT
            b.title "Title",
            ba.authors "Author(s)",
            r.start_date "Start",
            r.end_date "Finish",
            r.rating "Rating",
            r.end_date - r.start_date + 1 "Read Time"
        FROM reading r
        INNER JOIN books b
            on r.book_id = b.id
        INNER JOIN book_author_agg ba
            on b.id = ba.book_id
        {}
        ORDER BY
            r.end_date ASC NUllS Last
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