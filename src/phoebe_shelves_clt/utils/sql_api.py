""" Functions to interact with the PostgreSQL database

This module provides general convenience functions for interacting with the
PostgreSQL database.
"""

import sys
from typing import Tuple

import psycopg2
import pandas as pd

def connect_to_database(user: str, database: str):
    """ Connects to the PostgreSQL database

    Creates connection to the backend PostgreSQL database.

    Args:
        user: PostgreSQL username to acces the database.
        database: Name of the database to connect to.

    Todo: 
        * Add support for more server configuration variables
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
    """ Executes the provided SQL query

    Excutes the provided SQL query with the appropriate error messages, return
    values, and commit behavior.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        query: SQL query to execute.
        query_type: Type of query to indicate which execution behavior and
             error message to use.

    Returns:
        This function returns different values based on the type of the
        executed query.

        temp_df (DataFrame):
            A pandas DataFrame representation of the query output.
        results (List):
            List of row outputs from the query.

        For queries that make modifications to the database, the changes can
        be committed.
        
    Todo:
        * Rethink error messages and the minimum number of needed types.
            * Only have a single error message and rely on default expcetion
            * Condense down to "modify", "modify_return", "to_df", "to_list", "simple"
    """
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


def create_database(conn, db_name: str):
    """ Create a new PostgreSQL database

    Creates a new PostgreSQL database to use as the backend for the tools

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        db_name: Name of the new database.
    """
    query = f"create database {db_name}"
    execute_query(conn, query, "create_db")


def create_table(conn, query: str, table_name: str, force: bool):
    """ Create a new table in the PostgreSQL database

    Creates a new table with the appropriate columns/properties in the
    PostgreSQL database.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        query: Table creation query
        table_name: Name of the new table
        force: Indicator to overwrite (drop) an existing table before creating
            the new table. If not true, an existing table will not be
            overwritten.
    """

    if force:
        drop_table(conn, table_name)
    execute_query(conn, query, "create_table")


def drop_table(conn, table_name: str):
    """ Drop a table in the PostgreSQL database

    Drops a table if the PostgreSQL database if it already exists. This drop will
    also propogate additional modifications based on foreign keys (cascade).

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        table_name: Name of the new table
    """
    query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
    execute_query(conn, query, "drop_table")


def read_query(name: str):
    """ Read in a query from a separate SQL file

    Retrieves a query from a separate SQL file and stores it as a string for
    later execution. Query files are stored in the utils/sql_queries directory

    Args:
        name: Name of the SQL file to retreive

    Returns:
        (str): String representation of the full SQL query.
    """
    with open(f"src/phoebe_shelves_clt/sql_backend/sql_queries/{name}.sql") as f:
        return(f.read())


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

    result = execute_query(conn, query, "to_list")
    return(list(zip(*result))[0])