#!/usr/bin python

import psycopg2
import sys


def connect_to_server(configs):
    try:
        conn = psycopg2.connect(user=configs['user'])
    except Exception as e:
        print('Cannot connect to the server.')
        print(f'Error: {e}')
        sys.exit(1)
    else:
        print('Open connection successfully')
        cur = conn.cursor()
        return(conn, cur)


def connect_to_database(configs):
    try:
        conn = psycopg2.connect(user=configs['user'], database=configs['database'])
    except Exception as e:
        print('Cannot connect to the database.')
        print(f'Error: {e}')
        sys.exit(1)
    else:
        print('Successfully connected to database')
        cur = conn.cursor()
        return(conn, cur)


def create_database(conn, cur, db_name):
    conn.autocommit = True  # Required to create database

    query = f'CREATE DATABASE {db_name}'

    # Execution
    try:  # Need to catch in case query fails
        cur.execute(query)
    except Exception as e:
        print_error(e.pgcode)
        cur.close
    else:
        conn.autocommit = False


def print_error(err_code):
    if err_code == '42P04':
        print('Error: The database already exists.')

def select(cur, query):
    try:
        cur.execute(query)
        rows = cur.fetchall()
        return(rows)
    except Exception:
        print('Query failed.')


def main():
    configs = {'database': 'owl_shelves_clt',
               'user': 'anthonyagbay',
               'host': 'localhost'}
    # Connect to server
    # conn, cur = connect_to_server(configs)

    # if conn is not None:
    #     create_database(conn, cur, configs['database'])
    #     # Close Connection
    #     conn.close()

    conn, cur = connect_to_database(configs)

    if conn is not None:  # Only work if we successfully made a connection
        create_database(conn, cur, configs['database'])
        # query = 'SELECT title, release_year FROM film'
        # results = select(cur, query)
        # print(results[0])
    

if __name__ == '__main__':
    main()