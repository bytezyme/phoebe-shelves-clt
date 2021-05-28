""" Add, edit, or delete entries in the CSV backend database.

This module provides the primary functionality for adding, editing, or
deleting entries in the backend databases. The initial argument parsing methods
determine which database and mode to use while all other information is
request from the user using interactive prompts.

    Typical usage example:
        manage_csv(args.database, args.mode, model)

Todos:
    * Add support for using the series table
    * Add support for adding multiple authors/genres in the edit book function
    * Merge with SQL backend implementation
"""

from typing import Dict, Any, Union, List, Tuple

import numpy as np
import pandas as pd

from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.csv_backend import view_csv
from phoebe_shelves_clt import manage
from phoebe_shelves_clt.utils import data_model

CSVDataModel = data_model.CSVDataModel

### ------------- Selections ------------- ###

def select_author(model: CSVDataModel):
    """ Selects an author from the authors table and returns its ID.

    Prompts the user to begin providing author last name and compares
    it against existing authors. If there are now potentially existing authors,
    the user is prompted to create a new entry. If the author may already
    exist, they are provided the option to select from a potentia; list or
    create a new author.

    Args:
        model: Current CSVDataModel instance
    
    Returns:
        author_id (int): Unique ID of the selected author.
    """
    last_name, author_results = manage.prompt_for_author("csv", model)

    if len(author_results) == 0:
        author_id = add_author(model, last_name)
    else:
        author_options = list(author_results.keys()) + ["New Author"]
        author_select = inputs.prompt_from_choices(author_options)
        if author_select == "New Author":
            author_id = add_author(model, last_name)
        else:
            author_id = author_results[author_select]
    return(author_id)


def select_book(model: CSVDataModel) -> Tuple[str, int]:
    """ Selects a book from the books table and returns its ID.

    Prompts the user to provide an initial title and compares against existing
    books in the books table. If the book doesn't exist, the user can create a
    new entry. If the book may exist, the user will select from a list of
    possible options. They can select from the list or create a new entry from
    the title they initialy entered.

    Args:
        model: Current CSVDataModel instance
    
    Returns:
        A tuple containing the following information:

        title: The title that the user provided.
        book_id: Unique ID for the selected book.
    """
    title, title_results = manage.prompt_for_title("csv", model)

    if len(title_results) == 0:
        book_id = add_book(model, title)
    else:
        title_opts = list(title_results.keys()) + ["New Book"]
        title_select = inputs.prompt_from_choices(title_opts)
        if title_select == "New Book":
            book_id = add_book(model, title)
        else:
            book_id = title_results[title_select]
    return(title, book_id)


def select_genre(model: CSVDataModel) -> int:
    """ Selects a genre from the genres table and returns its ID.

    Prompts the user to select from the existing list of genres or to create
    a new genre.

    Args:
        model: Current CSVDataModel instance

    Returns:
        genre_id (int): Unique ID for the selected genre.
    """
    genres_dict = model.get_genres_dict()
    genre_options = list(genres_dict.keys()) + ["New Genre"]
    print("\nSelect from the following choices to choose a genre.")
    genre_select = inputs.prompt_from_choices(genre_options)

    if genre_select == "New Genre":
        new_genre = input("Please enter the new genre's name: ")
        genre_id = add_genre(model, new_genre)
    else:
        genre_id = genres_dict[genre_select]

    return(genre_id)



### –------------ Mange Authors ------------- ###


def add_author(model: CSVDataModel, last_name: str) -> int:
    """ Adds a new author to the author table

    Adds a new author to the authors table and new entries for all of the other
    tables, as needed.

    Args:
        model: Current CSVDataModel instance
        last_name: Last name of the author to add
        
    Returns:
        author_id: Unique ID of the new author entry.
    """

    cols_to_fill = ["last_name"]
    vals_to_fill = [last_name]

    first_name = input("Please enter the author's first name: ")
    middle_name = input("Please enter the author's middle name (Optional): ")
    suffix = input("Please enter the author's suffix (Optional): ")

    if first_name != "":
        cols_to_fill.append("first_name")
        vals_to_fill.append(first_name)
    if middle_name != "":
        cols_to_fill.append("middle_name")
        vals_to_fill.append(middle_name)
    if suffix != "":
        vals_to_fill.append(suffix)

    new_entry: Dict[str, Any] = dict(zip(cols_to_fill, vals_to_fill))
    entry_id = model.add_entry("authors", new_entry)

    return(entry_id)  # type: ignore - Cannot parse dynamic type


def edit_author(model: CSVDataModel, author_id: int):
    """ Edit an existing entry in the author table

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it generates and executes the correct
    update query to modify an existing author entry.

    Args:
        model: Current CSVDataModel instance
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
    model.edit_entry("authors", "id", author_id, cols_dict[col_select], new_value)


def delete_author(model: CSVDataModel, author_id: int):
    """ Delete a book entry from the author database

    Deletes the author entry associated with a given ID from the author table
    This deletion will cascade to all associated entries with the author ID in
    other tables in the database.

    Args:
        model: Current CSVDataModel instance
        author_id: ID of the author entry to delete
    """
    model.delete_entry("authors", "id", author_id)
    model.delete_entry("books_authors", "author_id", author_id)


def manage_authors_table(model: CSVDataModel, mode: str):
    """ Parent function for managing the entries in the authors table

    Controls the execution of different management modes for the authors table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        model: Current CSVDataModel instance
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    last_name, author_results = manage.prompt_for_author("csv", model)
    if mode == "add":
        if len(author_results) == 0:
            _ = add_author(model, last_name)
        else:
            print("")
            for author in author_results.keys():
                print(author)
            print("")
            if not inputs.confirm("Does the author appear in above list?"):
                _ = add_author(model, last_name)
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
                edit_author(model, author_id)
            else:
                delete_author(model, author_id)
        

### –------------ Mange Books ------------- ###

def add_book(model: CSVDataModel, title: str) -> int:
    """ Adds a new book to the database

    Adds a new book to the books table and new entries for all of the other 
    tables, as needed.

    Args:
        model: Current CSVDataModel instance
        title: Title of the new book.
        
    Returns:
        book_id: Unique ID of the new book entry.
    """
    author_id = select_author(model)
    pages = inputs.prompt_for_pos_int("Page length: ")
    rating = manage.prompt_for_rating("Rating (1-5) (Optional): ")
    genre_id = select_genre(model)

    #! Does not need same approach as adding a reading entry because there are
    #! only two potential query statements
    if rating is np.nan:
        new_entry = {"title": title, "book_length": pages}
    else:
        new_entry = {"title": title, "book_length": pages, "rating": rating}

    book_id = model.add_entry("books", new_entry)

    _ = model.add_entry("books_authors", {"book_id": book_id,
                                          "author_id": author_id})

    _ = model.add_entry("books_genres", {"book_id": book_id,
                                          "genre_id": genre_id})

    return(book_id)  # type: ignore - Cannot parse dynamic type

def edit_book(model:CSVDataModel, book_id: int):
    """ Edit an existing entry in the books database

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it runs the correct statements to make
    the modifications to the existing entry.

    Args:
        model: Current CSVDataModel instance
        book_id: ID of the book entry to modify.
    """
    cols = ["Title", "Author", "Pages", "Rating", "Genre"]
    print("\nWhich author property would you like to modify?")
    col_select = inputs.prompt_from_choices(cols)

    if col_select == "Title":
        new_title = input("\nWhat is the new title?: ")
        model.edit_entry("books", "id", book_id, "title", new_title)
    elif col_select == "Author":
        author_id = select_author(model)
        model.edit_entry("books_authors", "book_id", book_id, "author_id", author_id)
    elif col_select == "Pages":
        new_pages = inputs.prompt_for_pos_int("New page length: ")
        model.edit_entry("books", "id", book_id, "book_length", new_pages)
    elif col_select == "Rating":
        new_rating = manage.prompt_for_rating("New rating (1-5): ")
        model.edit_entry("books", "id", book_id, "rating", new_rating)
    elif col_select == "Genre":
        genre_id = select_genre(model)
        model.edit_entry("books_genres", "book_id", book_id, "genre_id", genre_id)

def delete_book(model: CSVDataModel, book_id: int):
    """ Delete a book entry from the books database

    Deletes the book entry associated with a given book ID from the books
    table. Separate functions are used to propagate the change through all
    other linked tables.

    Args:
        model: Current CSVDataModel instance
        book_id: ID of the book entry to delte.
    """

    model.delete_entry("books", "id", book_id)
    model.delete_entry("books_authors", "book_id", book_id)
    model.delete_entry("books_genres", "book_id", book_id)
    # model.delete_entry("books_series", "book_id", book_id)
    model.delete_entry("reading", "book_id", book_id)

def manage_books_table(model: CSVDataModel, mode: str):
    """ Parent function for managing the entries in the books table

    Controls the execution of different management modes for the books table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        model: Current CSVDataModel instance
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    title, results = manage.prompt_for_title("csv", model)

    if mode == "add":
        if len(results) == 0:
            add_book(model, title)
        else:
            to_edit_prompt = (f"\"{title}\" already exists in the books "
                              "database. Would you like to edit the entry?")
            if inputs.confirm(to_edit_prompt):
                edit_book(model, results[title])
 
    else:
        while len(results) == 0:
            print(f"\"{title}\" does not exist in the books database.")
            title, results = manage.prompt_for_title("csv", model)
        if mode == "edit":
            edit_book(model, results[title])
        else:
            delete_book(model, results[title])

### –------------ Mange Genres -------------- ###

def add_genre(model: CSVDataModel, genre_name) -> int:
    """ Add a new genre to the genre table

    Adds a new genre to the genre table. There is no need for additional
    checks for existing entries because upstream processes already contain
    those checks.

    Args:
        model: Current CSVDataModel instance
        name: Name of the new genre
    
    Returns:
        (int): Genre ID of the new genre
    """

    new_id = model.add_entry("genres", {"name": genre_name})
    return(new_id)  # type: ignore


def edit_genre(model: CSVDataModel, name: str, genre_id: int):
    """ Edit an existing entry in the genres table

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it runs the statements required to make
    the updates to the entry.

    Args:
        model: Current CSVDataModel instance
        entry_id: ID of the genre entry to edit.
    """
    model.edit_entry("genres", "id", genre_id, "name", name)


def delete_genre(model: CSVDataModel, genre_id: int):
    """ Delete a genre entry from the genres database

    Deletes the genre from the genres database. This deletion will propogate
    (cascade) to all other tables that reference the newly-deleted genre.

    Args:
        model: Current CSVDataModel instance
        genre_id: ID of the genre to delete.
    """
    model.delete_entry("genres", "id", genre_id)
    model.delete_entry("books_genres", "genre_id", genre_id)


def manage_genres_table(model: CSVDataModel, mode: str):
    """ Parent function for managing the entries in the genres table

    Controls the execution of different management modes for the genres table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        model: Current CSVDataModel instance
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    genre_name, genre_result = manage.prompt_for_genre("csv", model)

    if mode == "add":
        if len(genre_result) == 0:
            _ = add_genre(model, genre_name)
        else:
            print(f"\"{genre_name}\" already exists.")
    else:
        while len(genre_result) == 0:
            print(f"{genre_name} does not exist in the genres database")
            genre_name, genre_result = manage.prompt_for_genre("csv",model)

        if mode == "edit":
            genre_id = genre_result[genre_name]
            new_name = input("Please enter the new genre name: ")
            edit_genre(model, new_name, genre_id)
        else:
            delete_genre(model, genre_result[genre_name])


### –------------ Mange Reading ------------- ###

def add_reading_entry(model: CSVDataModel, book_id: int) -> int:
    """ Adds a new reading entry to the reading table

    Prompts the user for information to add a new reading entry to the 
    reading table. Then, generates the correct SQL query to insert a new
    entry with the given information and returns the ID of the new entry

    Args:
        model: Current CSVDataModel instance
        book_id: ID of the book to use for the new entry
    
    Returns:
        The ID of the new reading entry
    """
    print("Please enter the following optional information.")
    start = inputs.prompt_for_date("Start date: ")
    finish = inputs.prompt_for_date("Finish date: ")
    rating = manage.prompt_for_rating("Rating (1-5): ")

    new_entry = {"book_id": book_id}
    if start != "":
        new_entry["start_date"] = start  # type: ignore - Datetime
    if finish != "":
        new_entry["finish_date"] = finish  # type: ignore - Datetime
    if rating != "":
        new_entry["rating"] = rating  # type: ignore - Int/Float

    return(model.add_entry("reading", new_entry))  # type: ignore - Dynamic

def edit_reading_entry(model: CSVDataModel, title: str, id_list: List[int]):
    """ Edit an existing entry in the reading table

    Prompts the user to 1) select a property to modify and 2) provide the
    new value for the property. Then, it runs the neccessary statements to make
    modifications to the target entry.

    Args:
        model: Current CSVDataModel instance
        title: Title of the book to filter reading entries for.
        id_list: List of entry ID's associated with the given title
    """
    book_id_list = [model.get_books_dict(title)[title]]

    view_csv.print_table(model.generate_main_reading(filter="Title",
                                                     id_list=book_id_list),
                         show_index=True)

    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to edit: ",
                                         zero_indexed=True, use_index=False)

    prop_opts = ["Title", "Start", "Finish", "Rating"]
    print("\nWhich property would you like to edit?")
    prop_select = inputs.prompt_from_choices(prop_opts)

    if prop_select == "Title":
        _, book_id = select_book(model)
        model.edit_entry("reading", "id", edit_id, "book_id", book_id)

    elif prop_select in {"Start", "Finish"}:
        date = inputs.prompt_for_date(f"New {prop_select.lower()} date: ",
                                          as_string=True)
        col_name = "start_date" if prop_select == "Start" else "finish_date"
        model.edit_entry("reading", "id", edit_id, col_name, date)
    else:
        new_rating = manage.prompt_for_rating("New Rating: ")
        model.edit_entry("reading", "id", edit_id, "rating", new_rating)


def delete_reading_entry(model: CSVDataModel, title: str, id_list: List[int]):
    """ Delete a reading entry from the reading database

    Deletes the reading entry associated with a given entry ID from the reading
    table. This deletion will cascade to all associated entries with the
    book id as a foreign key.

    Args:
        model: Current CSVDataModel instance
        title: Title of the book to filter on
        id_list: List of entries associated with the title
    """
    book_id_list = [model.get_books_dict(title)[title]]

    view_csv.print_table(model.generate_main_reading(filter="Title",
                                                     id_list=book_id_list),
                         show_index=True)

    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to delete: ",
                                         zero_indexed=True, use_index=False)
    model.delete_entry("reading", "id", edit_id)

def manage_reading_table(model: CSVDataModel, mode: str):
    """ Parent function for managing the entries in the reading table

    Controls the execution of different management modes for the reading table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        model: Current CSVDataModel instance
        mode: Indicates whether to use the add, edit, or delete processes.
    """
    title, book_id = select_book(model)
    entry_id_list = model.get_reading_entries(book_id)

    if mode == "add":
        if len(entry_id_list) == 0:  # type: ignore
            add_reading_entry(model, book_id)
        else:
            to_edit_prompt = (f"There are existing entries for {title}. "
                               "Would you like to edit one of those entries?")
            if inputs.confirm(to_edit_prompt):
                edit_reading_entry(model, title, entry_id_list)  # type: ignore
            else:
                add_reading_entry(model, book_id)
    else:
        while len(entry_id_list) == 0:
            print(f"\"{title}\" does not have any associated reading entries.")
            title, book_id = select_book(model)
            entry_id_list = model.get_reading_entries(book_id)
        if mode == "edit":
            edit_reading_entry(model, title, entry_id_list)
        else:
            delete_reading_entry(model, title, entry_id_list)


### –------------ Mange Series -------------- ###


def manage_series_table(model: CSVDataModel, mode: str):
    """ Parent function for managing the entries in the series table

    Controls the execution of different management modes for the series table.
    Modes are selected via the initial command-line arguments and further
    information is requested via interactive prompts.

    Args:
        model: Underlying CSVDataModel instance
        mode: Indicates whether to use the add, edit, or delete processes.
    
    Todo:
        * Implement series mangement workflow
    """
    print("Series management is not available at this time.")

def main(db_select: str, mode: str, model: CSVDataModel):
    """ Main module function
    
    Main manage module function to launch different workflows to manage the
    different databases. Databases are first merged into a user-friendly
    presentation.
    
    Args:
        db_select: Which database to visualze.
        mode: Which visualization mode to utilize.
        model: Current CSVDataModel instance.

    Todo:
        * Implement series management
    """

    if db_select == "authors":
        manage_authors_table(model, mode)
    elif db_select == "books":
        manage_books_table(model, mode)
    elif db_select == "genres":
        manage_genres_table(model, mode)
    elif db_select == "reading":
        manage_reading_table(model, mode)
