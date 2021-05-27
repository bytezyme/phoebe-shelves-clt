""" Add, edit, or delete entries in the backend databases.

This module provides the primary functionality for adding, editing, or
deleting entries in the backend databases. The initial argument parsing methods
determine which database and mode to use while all other information is
request from the user using interactive prompts.

    Typical usage example:
        manage_sql(args.database, args.mode, dict(configs["SQL"]))

Todos:
    * Add support for using the series table
    * Add support for adding multiple authors/genres in the edit book function
"""

from typing import Dict, Tuple, List

import numpy as np

from phoebe_shelves_clt.utils import sql_api
from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.sql_backend import view_sql
from phoebe_shelves_clt.sql_backend import queries
from phoebe_shelves_clt import manage


### ----------- Getting Details --------------- ###

def get_reading_entries(conn, book_id: int) -> List:
    """ Retrieves reading entries associated with a book

    Retrieves reading entries associated with a given book by filtering
    the database based on the associated book ID.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        book_id: Book ID of the target book
    """
    query = f"SELECT id from reading where book_id = {book_id}"
    results = list(zip(*sql_api.execute_query(conn, query, "to_list")))

    if len(results) == 0:  # Sepcial case when no entries are in the table yet
        return([])
    else:
        return(list(results[0]))


### ------------- Selections ------------- ###

def select_author(conn):
    """ Selects an author from the authors table and returns its ID.

    Prompts the user to begin providing author last name and compares
    it against existing authors. If there are now potentially existing authors,
    the user is prompted to create a new entry. If the author may already
    exist, they are provided the option to select from a potentia llist or
    create a new author.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
    
    Returns:
        author_id (int): Unique ID of the selected author.
    """
    last_name, author_results = manage.prompt_for_author("sql", conn)

    if len(author_results) == 0:
        author_id = add_author(conn, last_name)
    else:
        author_options = list(author_results.keys()) + ["New Author"]
        author_select = inputs.prompt_from_choices(author_options)
        if author_select == "New Author":
            author_id = add_author(conn, last_name)
        else:
            author_id = author_results[author_select]
    return(author_id)


def select_book(conn) -> Tuple[str, int]:
    """ Selects a book from the books table and returns its ID.

    Prompts the user to provide an initial title and compares against existing
    books in the books table. If the book doesn't exist, the user can create a
    new entry. If the book may exist, the user will select from a list of
    possible options. They can select from the list or create a new entry from
    the title they initialy entered.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
    
    Returns:
        A tuple containing the following information:

        title: The title that the user provided.
        book_id: Unique ID for the selected book.
    """
    title, title_results = manage.prompt_for_title("sql", conn)

    if len(title_results) == 0:
        book_id = add_book(conn, title)
    else:
        title_opts = list(title_results.keys()) + ["New Book"]
        title_select = inputs.prompt_from_choices(title_opts)
        if title_select == "New Book":
            book_id = add_book(conn, title)
        else:
            book_id = title_results[title_select]
    return(title, book_id)  # type: ignore
        

def select_genre(conn):
    """ Selects a genre from the genres table and returns its ID.

    Prompts the user to select from the existing list of genres or to create
    a new genre.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.

    Returns:
        genre_id (int): Unique ID for the selected genre.
    """
    genres_dict = queries.retrieve_genres_list(conn)    
    genre_options = list(genres_dict.keys()) + ["New Genre"]
    print("\nSelect from the following choices to choose a genre.")
    genre_select = inputs.prompt_from_choices(genre_options)

    if genre_select == "New Genre":
        new_genre = input("Please enter the new genre's name: ")
        genre_id = add_genre(conn, new_genre)
    else:
        genre_id = genres_dict[genre_select]

    return(genre_id)


### –------------ Mange Books ------------- ###

def add_book(conn, title: str):
    """ Adds a new book to the database

    Adds a new book to the books table and new entries for all of the other 
    tables, as needed.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        title: Title of the new book.
        
    Returns:
        book_id (int): Unique ID of the new book entry.
    """
    # Prompting for additional properties
    author_id = select_author(conn)
    pages = inputs.prompt_for_pos_int("Page length: ")
    rating = manage.prompt_for_rating("Rating (1-5) (Optional): ")
    genre_id = select_genre(conn)

    #! Does not need same approach as adding a reading entry because there are
    #! only two potential query statements
    if rating is np.nan:
        books_query = ("INSERT INTO books(title, book_length) "
                     f"VALUES('{title}', {pages}) RETURNING id;")
    else:
        books_query = ("INSERT INTO books(title, book_length, rating) "
                     f"VALUES('{title}', {pages}, {rating}) RETURNING id;")

    book_id = sql_api.execute_query(conn, books_query, "modify_return")[0][0]

    books_authors_query = ("INSERT INTO books_authors(book_id, author_id) "
                            f"VALUES({book_id}, {author_id})")
    sql_api.execute_query(conn, books_authors_query, "modify")

    books_genres_query = ("INSERT INTO books_genres(book_id, genre_id) "
                          f"VALUES({book_id}, {genre_id})")
    sql_api.execute_query(conn, books_genres_query, "modify")

    return(book_id)

def edit_book(conn, book_id: int):
    """ Edit an existing entry in the books database

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it generates and executes the correct
    update query to modify an existing book entry.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        book_id: ID of the book entry to modify.
    """
    cols = ["Title", "Author", "Pages", "Rating", "Genre"]
    print("\nWhich author property would you like to modify?")
    col_select = inputs.prompt_from_choices(cols)
    if col_select == "Title":
        new_title = input("\nWhat is the new title?: ")
        query = sql_api.read_query("update_book").format("title",
                                                         f"'{new_title}'",
                                                         book_id)
    elif col_select == "Author":
        author_id = select_author(conn)
        query = sql_api.read_query("update_books_authors").format(author_id,
                                                                  book_id)
        query = query.format(author_id, book_id)
    
    elif col_select == "Pages":
        new_pages = inputs.prompt_for_pos_int("New page Length: ")
        query = sql_api.read_query("update_book").format("book_length",
                                                          new_pages,
                                                          book_id)
    elif col_select == "Rating":
        new_rating = manage.prompt_for_rating("New rating (1-5): ")
        query = sql_api.read_query("update_book").format("rating",
                                                         new_rating,
                                                         book_id)
    elif col_select == "Genre":
        genre_id = select_genre(conn)
        query = sql_api.read_query("update_books_genres").format(genre_id,
                                                                 book_id)

    sql_api.execute_query(conn, query, "modify") # type: ignore

def delete_book(conn, book_id: int):
    """ Delete a book entry from the books database

    Deletes the book entry associated with a given book ID from the books
    table. This deletion will cascade to all associated entries with the
    book id as a foreign key.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        book_id: ID of the book entry to delte.
    """
    query = f"DELETE FROM books where id = {book_id}"
    sql_api.execute_query(conn, query, "modify")

def manage_books_table(conn, mode: str):
    """ Parent function for managing the entries in the books table

    Controls the execution of different management modes for the books table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    title, results = manage.prompt_for_title("sql", conn)
    
    if mode == "add":
        if len(results) == 0:
            add_book(conn, title)
        else:
            to_edit_prompt = (f"\"{title}\" already exists in the books "
                              "database. Would you like to edit the entry?")
            if inputs.confirm(to_edit_prompt):
                edit_book(conn, results[title])
 
    else:
        while len(results) == 0:
            print(f"\"{title}\" does not exist in the books database.")
            title, results = manage.prompt_for_title("sql", conn)
        if mode == "edit":
            edit_book(conn, results[title])
        else:
            delete_book(conn, results[title])


### –------------ Mange Reading ------------- ###

def add_reading_entry(conn, book_id: int) -> int:
    """ Adds a new reading entry to the reading table

    Prompts the user for information to add a new reading entry to the 
    reading table. Then, generates the correct SQL query to insert a new
    entry with the given information and returns the ID of the new entry

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        book_id: ID of the book to use for the new entry
    
    Returns:
        The ID of the new reading entry
    """
    print("Please enter the following optional information.")
    start = inputs.prompt_for_date("Start date: ", as_string=True)
    finish = inputs.prompt_for_date("Finish date: ", as_string=True)
    rating = manage.prompt_for_rating("Rating (1-5): ")

    cols_to_fill = ["book_id"]
    vals_to_fill = [str(book_id)]

    if start != "":
        cols_to_fill.append("start_date")
        vals_to_fill.append(f"'{start}'")
    if finish != "":
        cols_to_fill.append("finish_date")
        vals_to_fill.append(f"'{finish}'")
    if rating is not np.nan:
        cols_to_fill.append("rating")
        vals_to_fill.append(str(rating))

    cols_string = ", ".join(cols_to_fill)
    vals_string = ", ".join(vals_to_fill)
    query = ("INSERT INTO reading({}) VALUES({}) "
             "RETURNING id").format(cols_string, vals_string)
    return(sql_api.execute_query(conn, query,
                                 "modify_return")[0][0])  # type: ignore
    

def edit_reading_entry(conn, title: str, id_list: List[int]):
    """ Edit an existing entry in the reading table

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it generates and executes the correct
    update query to modify an existing reading entry.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        title: Title of the book to filter reading entries for.
        id_list: List of entry ID's associated with the given title
    """
    vis_query = ("SELECT * FROM reading_friendly rf where "
                 "rf.\"Title\" ILIKE '{}'").format(title)
    view_sql.print_table(conn, vis_query)
    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to edit: ",
                                         zero_indexed=True, use_index=False)

    prop_opts = ["Title", "Start", "Finish", "Rating"]
    print("\nWhich property would you like to edit?")
    prop_select = inputs.prompt_from_choices(prop_opts)

    if prop_select == "Title":
        title, book_id = select_book(conn)
        edit_query = sql_api.read_query("update_reading").format("book_id",
                                                                 book_id,
                                                                 edit_id)

    elif prop_select in {"Start", "Finish"}:
        date = inputs.prompt_for_date(f"New {prop_select.lower()} date: ",
                                          as_string=True)
        col_name = "start_date" if prop_select == "Start" else "finish_date"
        edit_query = sql_api.read_query("update_reading").format(col_name,
                                                                 f"'{date}'",
                                                                 edit_id)

    else:
        new_rating = manage.prompt_for_rating("New Rating: ")
        edit_query = sql_api.read_query("update_reading").format("rating",
                                                                 new_rating,
                                                                 edit_id)

    sql_api.execute_query(conn, edit_query, "modify")


def delete_reading_entry(conn, title, id_list):
    """ Delete a book entry from the reading database

    Deletes the reading entry associated with a given entry ID from the reading
    table. This deletion will cascade to all associated entries with the
    book id as a foreign key.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        title: Title of the book to filter on
        id_list: List of entries associated with the title
    """
    vis_query = ("SELECT * FROM reading_friendly rf where "
                 "rf.\"Title\" ILIKE '{}'").format(title)
    view_sql.print_table(conn, vis_query)
    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to delete: ",
                                         zero_indexed=True, use_index=False)
    delete_query = f"DELETE FROM reading where id = {edit_id}"
    sql_api.execute_query(conn, delete_query, "modify")


def manage_reading_table(conn, mode):
    """ Parent function for managing the entries in the reading table

    Controls the execution of different management modes for the reading table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    # Load in temporary reading_friendly
    initial_load_query = queries.main_reading_query()
    sql_api.execute_query(conn, initial_load_query, "basic")

    # First select a valid book and filter the reading_entries
    title, book_id = select_book(conn)
    entry_id_list = get_reading_entries(conn, book_id)

    if mode == "add":
        if len(entry_id_list) == 0:  # type: ignore
            add_reading_entry(conn, book_id)
        else:
            to_edit_prompt = (f"There are existing entries for {title}. "
                               "Would you like to edit one of those entries?")
            if inputs.confirm(to_edit_prompt):
                edit_reading_entry(conn, title, entry_id_list)  # type: ignore
            else:
                add_reading_entry(conn, book_id)
    else:
        while len(entry_id_list) == 0:
            print(f"\"{title}\" does not have any associated reading entries.")
            title, book_id = select_book(conn)
            entry_id_list = get_reading_entries(conn, book_id)
        if mode == "edit":
            edit_reading_entry(conn, title, entry_id_list)
        else:
            delete_reading_entry(conn, title, entry_id_list)


### –------------ Mange Authors ------------- ###

def add_author(conn, last_name: str) -> int:
    """ Adds a new author to the author table

    Adds a new author to the authors table and new entries for all of the other
    tables, as needed.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        last_name: Last name of the author to add
        
    Returns:
        author_id (int): Unique ID of the new author entry.
    """

    cols_to_fill = ["last_name"]
    vals_to_fill = [f"'{last_name}'"]

    first_name = input("Please enter the author's first name: ")
    middle_name = input("Please enter the author's middle name (Optional): ")
    suffix = input("Please enter the author's suffix (Optional): ")

    if first_name != "":
        cols_to_fill.append("first_name")
        vals_to_fill.append(f"'{first_name}'")
    if middle_name != "":
        cols_to_fill.append("middle_name")
        vals_to_fill.append(f"'{middle_name}'")
    if suffix != "":
        cols_to_fill.append("suffix")
        vals_to_fill.append(f"'{suffix}'")

    cols_string = ", ".join(cols_to_fill)
    vals_string = ", ".join(vals_to_fill)
    query = sql_api.read_query("add_author").format(cols_string, vals_string)
    author_id = sql_api.execute_query(conn, query, "modify_return")[0][0]
    return(author_id)  # type: ignore


def edit_author(conn, author_id: int):
    """ Edit an existing entry in the author table

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it generates and executes the correct
    update query to modify an existing author entry.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        author_id: ID of the author entry to edit.
    """
    cols_dict = {
        "First Name": "first_name",
        "Middle Name": "middle_name",
        "Last Name": "last_name",
        "Suffix": "suffix"
    }

    print("\nWhich author property would you like to modify?")
    col_select = inputs.prompt_from_choices(list(cols_dict.keys()))
    new_value = input(f"\nWhat is the new {col_select.lower()}?: ")
    query = (f"UPDATE authors SET {cols_dict[col_select]} = '{new_value}' "
              "WHERE id = {author_id}")
    query = sql_api.read_query("update_author").format(cols_dict[col_select],
                                                       new_value, author_id)
    sql_api.execute_query(conn, query, "modify")


def delete_author(conn, author_id: int):
    """ Delete a book entry from the author database

    Deletes the author entry associated with a given ID from the author table
    This deletion will cascade to all associated entries with the author ID in
    other tables in the database.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        author_id: ID of the author entry to delete
    """
    query = f"DELETE FROM authors WHERE id = {author_id}"
    sql_api.execute_query(conn, query, "modify")


def manage_authors_table(conn, mode: str):
    """ Parent function for managing the entries in the authors table

    Controls the execution of different management modes for the authors table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    last_name, author_results = manage.prompt_for_author("sql", conn)
    if mode == "add":
        if len(author_results) == 0:
            add_author(conn, last_name)
        else:
            print("")
            for author in author_results.keys():
                print(author)
            print("")
            if not inputs.confirm("Does the author appear in above list?"):
                _ = add_author(conn, last_name)
            else:
                print("Cannot add a duplicate author to the database.")
    else:
        if len(author_results) == 0:
            print("There are no existing authors with that last name.")
        else:
            author_options = list(author_results.keys())
            author_select = inputs.prompt_from_choices(author_options)
            author_id = author_results[author_select]
            if mode == "edit":
                edit_author(conn, author_id)
            else:
                delete_author(conn, author_id)


### –------------ Mange Series -------------- ###

def manage_series_table(conn, mode: str):
    """ Parent function for managing the entries in the series table

    Controls the execution of different management modes for the series table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        mode: Indicates whether to use the add, edit, or delete processes.
    
    Todo:
        * Implement series mangement workflow
    """
    pass


### –------------ Mange Genres -------------- ###

def add_genre(conn, name: str) -> int:
    """ Add a new genre to the genre table

    Args:
        conn (psycopg2.connection): Connection to PostgreSQL table
        name: Name of the new genre
    
    Returns:
        (int): Genre ID of the new genre
    """
    query = f"INSERT INTO genres(name) VALUES('{name}') RETURNING id;"
    return(sql_api.execute_query(\
        conn, query, "modify_return")[0][0])  # type: ignore


def edit_genre(conn, name: str, entry_id: int):
    """ Edit an existing entry in the genres table

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it generates and executes the correct
    update query to modify an existing genre entry.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        entry_id: ID of the genre entry to edit.
    """
    query = f"UPDATE genres SET name = '{name}' WHERE id = {entry_id}"
    sql_api.execute_query(conn, query, "modify")


def delete_genre(conn, genre_id):
    """ Delete a genre entry from the genres database

    Deletes the genre from the genres database. This deletion will propogate
    (cascade) to all other tables that reference the newly-deleted genre.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        name: Name of the genre to delete.
    """
    query = f"DELETE FROM genres WHERE id = {genre_id}"
    sql_api.execute_query(conn, query, "modify")


def manage_genres_table(conn, mode: str):
    """ Parent function for managing the entries in the genres table

    Controls the execution of different management modes for the genres table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    genre_name, genre_result = manage.prompt_for_genre("sql", conn)

    if mode == "add":
        if len(genre_result) == 0: 
            _ = add_genre(conn, genre_name)
        else:
            print(f"\"{genre_name}\" already exists.")

    else:
        while len(genre_result) == 0:
            print(f"{genre_name} does not exist in the genres database")
            genre_name, genre_result = manage.prompt_for_genre("sql", conn)

        if mode == "edit":
            genre_id = genre_result[genre_name]
            new_name = input("Please enter the new genre name: ")
            edit_genre(conn, new_name, genre_id)
        else:
            delete_genre(conn, genre_result[genre_name])

  
### ------------- Main Function ------------- ###

def main(db_select: str, mode: str, sql_configs: Dict[str, str]):
    """ Main module function
    
    Main manage module function to launch different workflows to manage the
    different databases. Databases are first merged into a user-friendly
    presentation.
    
    Args:
        db_select: Which database to visualze.
        mode: Which visualization mode to utilize
        sql_configs: Configurations for the PostgreSQL database

    Todo:
        * Implement series management
    """
    conn = sql_api.connect_to_database(sql_configs["user"],
                                    sql_configs["database"])

    if db_select == "books":
        manage_books_table(conn, mode)
    elif db_select == "authors":
        manage_authors_table(conn, mode)
    elif db_select == "genres":
        manage_genres_table(conn, mode)
    elif db_select == "reading":
        manage_reading_table(conn, mode)
    