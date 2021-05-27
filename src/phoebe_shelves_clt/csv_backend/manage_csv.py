from typing import Tuple, Dict, Any, Union, List

import numpy as np
import pandas as pd

from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.csv_backend import view_csv
from phoebe_shelves_clt import manage
from phoebe_shelves_clt.utils import data_model

CSVDataModel = data_model.CSVDataModel

### ----------- Getting Details --------------- ###

def prompt_for_title(model: CSVDataModel) -> Tuple[str, Dict]:
    title = input("Please enter the book title: ")
    title_results = model.get_books_dict(title)
    return(title, title_results)

def prompt_for_author(model: CSVDataModel) -> Tuple[str, Dict]:
    last_name = input("Please enter the author's last name: ")
    author_results = model.get_authors_dict(last_name)
    return(last_name, author_results)

def prompt_for_genre(model: CSVDataModel) -> Tuple[str, Dict[str, int]]:
    genre_name = input("Please enter the genre name: ")
    genre_results = model.get_genres_dict(genre_name)
    return(genre_name, genre_results)


### ------------- Selections ------------- ###

def select_author(model):
    last_name, author_results = prompt_for_author(model)

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

def select_genre(model: CSVDataModel):
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

def select_book(model: CSVDataModel):
    title, title_results = prompt_for_title(model)

    if len(title_results) == 0:
        book_id = add_book(model, title)
    else:
        title_opts = list(title_results.keys()) + ["New Book"]
        title_select = inputs.prompt_from_choices(title_opts)
        if title_select == "New Book":
            book_id = add_book(model, title)
        else:
            book_id = title_results[title_select]
    return(title, book_id)  # type: ignore

### –------------ Mange Authors ------------- ###


def add_author(model: CSVDataModel, last_name, backend="csv"):
    """

    Todo:
        * Need better way of formatting the names to work with both backends
    """

    cols_to_fill = ["last_name"]
    val = f"'{last_name}'" if backend == "sql" else last_name
    vals_to_fill = [val]

    first_name = input("Please enter the author's first name: ")
    middle_name = input("Please enter the author's middle name (Optional): ")
    suffix = input("Please enter the author's suffix (Optional): ")

    if first_name != "":
        cols_to_fill.append("first_name")
        val = f"'{first_name}'" if backend == "sql" else first_name
        vals_to_fill.append(val)
    if middle_name != "":
        cols_to_fill.append("middle_name")
        val = f"'{middle_name}'" if backend == "sql" else middle_name
        vals_to_fill.append(val)
    if suffix != "":
        val = f"'{suffix}'" if backend == "sql" else suffix
        vals_to_fill.append(val)

    new_entry: Dict[str, Any] = dict(zip(cols_to_fill, vals_to_fill))
    entry_id = model.add_entry("authors", new_entry)

    return(entry_id)  # type: ignore


def edit_author(model: CSVDataModel, author_id):
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


def delete_author(model: CSVDataModel, author_id):

    # Delete entry in authors table
    model.delete_entry("authors", "id", author_id)

    # Delete entry in books_authors table
    model.delete_entry("books_authors", "author_id", author_id)


def manage_authors_table(model: CSVDataModel, mode: str):
    last_name, author_results = prompt_for_author(model)
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

    return(book_id)  # type: ignore

def edit_book(model:CSVDataModel, book_id: int):
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
    """ Deletes a book and all dependencies

    To delete a book you must cascade the following:
    1) books_authors
    2) books_genres
    3) books_series
    4) reading
    """

    model.delete_entry("books", "id", book_id)
    model.delete_entry("books_authors", "book_id", book_id)
    model.delete_entry("books_genres", "book_id", book_id)
    # model.delete_entry("books_series", "book_id", book_id)
    model.delete_entry("reading", "book_id", book_id)

def manage_books_table(model: CSVDataModel, mode: str):
    title, results = prompt_for_title(model)

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
            title, results = prompt_for_title(model)
        if mode == "edit":
            edit_book(model, results[title])
        else:
            delete_book(model, results[title])

### –------------ Mange Genres -------------- ###

def add_genre(model: CSVDataModel, genre_name) -> Union[int, None]:
    """ Add a new genre to the genre table

    Adds a new genre entry to the genre table. This method does not
    need to check for an existing entry because those checks are done
    when processing user input.
    """

    new_id = model.add_entry("genres", {"name": genre_name})
    return(new_id)


def edit_genre(model: CSVDataModel, name: str, genre_id: int):
    model.edit_entry("genres", "id", genre_id, "name", name)


def delete_genre(model: CSVDataModel, genre_id):
    # Delete entry in genres table
    model.delete_entry("genres", "id", genre_id)

    # Delete entry in books_genres table
    model.delete_entry("books_genres", "genre_id", genre_id)


def manage_genres_table(model: CSVDataModel, mode: str):
    genre_name, genre_result = prompt_for_genre(model)

    if mode == "add":
        if len(genre_result) == 0:
            _ = add_genre(model, genre_name)
        else:
            print(f"\"{genre_name}\" already exists.")
    else:
        while len(genre_result) == 0:
            print(f"{genre_name} does not exist in the genres database")
            genre_name, genre_result = prompt_for_genre(model)

        if mode == "edit":
            genre_id = genre_result[genre_name]
            new_name = input("Please enter the new genre name: ")
            edit_genre(model, new_name, genre_id)
        else:
            delete_genre(model, genre_result[genre_name])


### –------------ Mange Reading ------------- ###

def add_reading_entry(model: CSVDataModel, book_id):
    print("Please enter the following optional information.")
    start = inputs.prompt_for_date("Start date: ")
    finish = inputs.prompt_for_date("Finish date: ")
    rating = manage.prompt_for_rating("Rating (1-5): ")

    new_entry = {"book_id": book_id}
    if start != "":
        new_entry["start_date"] = start
    if finish != "":
        new_entry["finish_date"] = finish
    if rating != "":
        new_entry["rating"] = rating

    return(model.add_entry("reading", new_entry))

def edit_reading_entry(model: CSVDataModel, title: str, id_list: List[int]):
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
    book_id_list = [model.get_books_dict(title)[title]]

    view_csv.print_table(model.generate_main_reading(filter="Title",
                                                     id_list=book_id_list),
                         show_index=True)

    edit_id = inputs.prompt_from_choices(id_list, "Choose an entry to delete: ",
                                         zero_indexed=True, use_index=False)
    model.delete_entry("reading", "id", edit_id)

def manage_reading_table(model: CSVDataModel, mode: str):
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
        conn (psycopg2.connection): Connection to the PostgreSQL database.
        mode: Indicates whether to use the add, edit, or delete processes.
    
    Todo:
        * Implement series mangement workflow
    """

def main(db_select: str, mode: str, model: CSVDataModel):

    if db_select == "authors":
        manage_authors_table(model, mode)
    elif db_select == "books":
        manage_books_table(model, mode)
    elif db_select == "genres":
        manage_genres_table(model, mode)
    elif db_select == "reading":
        manage_reading_table(model, mode)
