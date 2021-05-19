from typing import Dict, Tuple
import numpy as np

from ..utils import sql_api
from ..utils import inputs
from . import view_sql


### –------------ Mange Books --------------- ###

def prompt_for_rating(prompt):
    """Prompt user for an integer rating (max 5)

    Args:
        prompt {string} -- Prompt that user sees on the command line

    Outputs:
        rating {int} -- Intger rating or np.nan if empty string is passed
    """

    rating = input(prompt)

    while rating not in {'', '1', '2', '3', '4', '5'}:
        rating = input('Choose an integer between 1 and 5 or leave blank: ')

    # Format rating
    rating = int(rating) if rating != "" else np.nan
    return(rating)

def prompt_for_title(conn) -> Tuple[str, Dict]:
    """

    - New books require: 1) title, 2) author, 3) length, 4) series (opt), 5) rating (opt), 6) genre
 
    1. Prompt for any title search string
    2. If result query returns 0: the title doesn't exist, so you will have to create a new book
    3. If result query >0: There are already potential existing matches. Select a match from the selection
       to begin editing or create a new entry
    """
    title = input("Please enter the book title: ")
    query = f"SELECT title, id FROM books WHERE title ILIKE '{title}'"
    query_results = dict(sql_api.execute_query(conn, query,
                                               "to_list"))  # type: ignore
    return(title, query_results)

def select_author(conn):
    last_name, author_results = prompt_for_author(conn)

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

def select_book(conn):
    title, title_results = prompt_for_title(conn)

    if len(title_results) == 0:
        book_id = add_book(conn, title)
    else:
        title_opts = list(title_results.keys()) + ["New Book"]
        title_select = inputs.prompt_from_choices(title_opts)
        if title_select == "New Book":
            book_id = add_book(conn, title)
        else:
            book_id = title_results[title_select]
    return(title, book_id)
        

def select_genre(conn):
    genres_dict = sql_api.retrieve_genres_list(conn)    
    genre_options = list(genres_dict.keys()) + ["New Genre"]
    print("\nSelect from the following choices to choose a genre.")
    genre_select = inputs.prompt_from_choices(genre_options)

    if genre_select == "New Genre":
        new_genre = input("Please enter the new genre's name: ")
        genre_id = add_genre(conn, new_genre)
    else:
        genre_id = genres_dict[genre_select]

    return(genre_id)

def add_book(conn, title: str):
    """
    """
    # Author Information
    author_id = select_author(conn)

    # Filling in Pages Information
    _, pages = inputs.prompt_for_pos_int("Page length: ")

    # Requesting Rating Information
    rating = prompt_for_rating("Rating (1-5) (Optional): ")

    # Genre
    genre_id = select_genre(conn)

    # Add new books table entry
    if rating is np.nan:
        books_query = ("INSERT INTO books(title, book_length) "
                     f"VALUES('{title}', {pages}) RETURNING id;")
    else:
        books_query = ("INSERT INTO books(title, book_length, rating) "
                     f"VALUES('{title}', {pages}, {rating}) RETURNING id;")

    # Add new book entry into books table
    book_id = sql_api.execute_query(conn, books_query, "modify_return")[0][0]

    # Add new books_authors table entry
    books_authors_query = ("INSERT INTO books_authors(book_id, author_id) "
                            f"VALUES({book_id}, {author_id})")
    sql_api.execute_query(conn, books_authors_query, "modify")

    # Add new books_genres table entry
    books_genres_query = ("INSERT INTO books_genres(book_id, genre_id) "
                          f"VALUES({book_id}, {genre_id})")
    sql_api.execute_query(conn, books_genres_query, "modify")

    return(book_id)

def edit_book(conn, book_id: int):
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
        query = (f"UPDATE books_authors SET author_id = {author_id} where book_id = {book_id}")
    
    elif col_select == "Pages":
        _, new_pages = inputs.prompt_for_pos_int("New page Length: ")
        query = sql_api.read_query("update_book").format("book_length",
                                                          new_pages,
                                                          book_id)
    elif col_select == "Rating":
        new_rating = prompt_for_rating("New rating (1-5): ")
        query = sql_api.read_query("update_book").format("rating",
                                                         new_rating,
                                                         book_id)
    elif col_select == "Genre":
        genre_id = select_genre(conn)
        query = (f"UPDATE books_genres SET genre_id = {genre_id} where book_id = {book_id}")

    sql_api.execute_query(conn, query, "modify") # type: ignore

def remove_book(conn, book_id: int):
    query = f"DELETE FROM books where id = {book_id}"
    sql_api.execute_query(conn, query, "modify")

def manage_books_table(conn, mode):
    """
    """
    title, results = prompt_for_title(conn)
    
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
            title, results = prompt_for_title(conn)
        if mode == "edit":
            edit_book(conn, results[title])
        else:
            remove_book(conn, results[title])

### –------------ Mange Reading ------------- ###


def prompt_for_reading_entry(conn, book_id):
    query = f"SELECT id from reading where book_id = {book_id}"
    results = list(zip(*sql_api.execute_query(conn, query, "to_list")))[0]
    return(list(results))

def add_reading_entry(conn, book_id):
    print("Please enter the following optional information.")
    start, _ = inputs.prompt_for_date("Start date: ")
    finish, _ = inputs.prompt_for_date("Finish date: ")
    rating = prompt_for_rating("Rating (1-5): ")

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

    query = f"INSERT INTO reading({cols_string}) VALUES({vals_string}) RETURNING id"
    return(sql_api.execute_query(conn, query, "modify_return")[0][0])
    

def edit_reading_entry(conn, title, id_list):
    # id_str = "(" + ", ".join([str(id) for id in id_list]) + ")"
    vis_query = f"SELECT * FROM reading_friendly rf where rf.\"Title\" ILIKE '{title}'"
    view_sql.print_table(conn, vis_query)
    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to edit: ",
                                         zero_indexed=True, use_index=False)
    prop_opts = ["Title", "Start", "Finish", "Rating"]
    print("\nWhich property would you like to edit?")
    prop_select = inputs.prompt_from_choices(prop_opts)

    if prop_select == "Title":
        title, book_id = select_book(conn)
        edit_query = f"UPDATE reading SET book_id = {book_id} where id = {edit_id}"
    elif prop_select in {"Start", "Finish"}:
        new_date, _ = inputs.prompt_for_date(f"New {prop_select.lower()} date: ")
        col_name = "start_date" if prop_select == "Start" else "finish_date"
        edit_query = f"Update reading SET {col_name} = '{new_date}' WHERE id = {edit_id}"
    else:
        new_rating = prompt_for_rating("New Rating: ")
        edit_query = f"UPDATE reading SET rating = {new_rating} where id = {edit_id}"

    sql_api.execute_query(conn, edit_query, "modify")




def delete_reading_entry(conn, title, id_list):
    vis_query = f"SELECT * FROM reading_friendly rf where rf.\"Title\" ILIKE '{title}'"
    view_sql.print_table(conn, vis_query)
    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to edit: ",
                                         zero_indexed=True, use_index=False)
    delete_query = f"DELETE FROM reading where id = {edit_id}"
    sql_api.execute_query(conn, delete_query, "modify")

def manage_reading_table(conn, mode):
    # Load in temporary reading_friendly
    initial_load_query = sql_api.query_reading()
    sql_api.execute_query(conn, initial_load_query, "basic")

    # First select a valid book and filter the reading_entries
    title, book_id = select_book(conn)
    entry_id_list = prompt_for_reading_entry(conn, book_id)

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
            entry_id_list = prompt_for_reading_entry(conn, book_id)
        if mode == "edit":
            edit_reading_entry(conn, title, entry_id_list)
        else:
            delete_reading_entry(conn, title, entry_id_list)

### –------------ Mange Authors ------------- ###

def prompt_for_author(conn):
    last_name = input("Please enter the author's last name: ")
    author_query = (sql_api.read_query('author_filter').format(last_name))
    author_results = dict(sql_api.execute_query(conn, author_query, "to_list"))  # type: ignore
    return(last_name, author_results)

def add_author(conn, last_name: str):
    first_name = input("Please enter the author's first name: ")
    middle_name = input("Please enter the author's middle name (Optional): ")
    suffix = input("Please enter the author's suffix (Optional): ")
    query = sql_api.read_query("add_author").format(first_name,
                                                    middle_name,
                                                    last_name,
                                                    suffix)
    return(sql_api.execute_query(conn, query, "modify_return")[0][0])

def edit_author(conn, author_id):
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
    query = sql_api.read_query("update_author").format(cols_dict[col_select], new_value, author_id)
    sql_api.execute_query(conn, query, "modify")

def delete_author(conn, author_id):
    query = f"DELETE FROM authors WHERE id = {author_id}"
    sql_api.execute_query(conn, query, "modify")

def manage_authors_table(conn, mode):
    last_name, author_results = prompt_for_author(conn)
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


### ------------- Manage Series ------------- ###

def manage_series_table():
    pass

### –------------ Mange Genres -------------- ###

def add_genre(conn, name: str):
    """ Add a new genre to the genre table

    Args:
        conn (psycopg2.connection): Connection to PostgreSQL table
        name: Name of the new genre
    
    Returns:
        (int): Genre ID of the new genre
    """
    query = f"INSERT INTO genres(name) VALUES('{name}') RETURNING id;"
    return(sql_api.execute_query(conn, query, "modify_return")[0][0])

def edit_genre(conn, name: str, id: int):
    query = f"UPDATE genres SET name = '{name}' WHERE id = {id}"
    sql_api.execute_query(conn, query, "modify")

def delete_genre(conn, name: str):
    query = f"DELETE FROM genres WHERE name = '{name}'"
    sql_api.execute_query(conn, query, "modify")

def prompt_for_genre(conn):
    genre_name = input("Please enter the genre name: ")
    genre_query = f"SELECT name, id from genres where name ilike '{genre_name}'"
    genre_result = dict(sql_api.execute_query(conn, genre_query, "to_list"))  # type: ignore
    return(genre_name, genre_result)

def manage_genres_table(conn, mode: str):
    genre_name, genre_result = prompt_for_genre(conn)

    if mode == "add":
        if len(genre_result) == 0: 
            _ = add_genre(conn, genre_name)
        else:
            print(f"\"{genre_name}\" already exists.")

    else:
        while len(genre_result) == 0:
            print(f"{genre_name} does not exist in the genres database")
            genre_name, genre_result = prompt_for_genre(conn)

        if mode == "edit":
            genre_id = genre_result[genre_name]
            new_name = input("Please enter the new genre name: ")
            edit_genre(conn, new_name, genre_id)
        else:
            delete_genre(conn, genre_name)
        
### ------------- Main Function ------------- ###

def manage_sql(db_select: str, mode: str, sql_configs: Dict[str, str]):
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
    