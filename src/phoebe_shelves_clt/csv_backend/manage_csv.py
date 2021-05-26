from typing import Tuple, Dict, Any

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

def prompt_for_genre(model: CSVDataModel) -> Tuple[str, Dict]:
    genre_name = input("Please enter the genre name: ")
    genre_results = model.get_genres_dict(genre_name)
    return(genre_name, genre_results)


### ------------- Selections ------------- ###

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

    cols_to_fill.append("id")
    new_entry: Dict[str, Any] = dict(zip(cols_to_fill, vals_to_fill))
    new_entry["id"] = model.generate_id("authors")
    model.add_entry("authors", new_entry)

    return(new_entry["id"])  # type: ignore


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
    model.delete_entry("authors", author_id)


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


def manage_books_table(model: CSVDataModel, mode: str):
    pass

### –------------ Mange Genres -------------- ###

def add_genre(model: CSVDataModel, genre_name) -> int:
    """ Add a new genre to the genre table

    Adds a new genre entry to the genre table. This method does not
    need to check for an existing entry because those checks are done
    when processing user input.
    """

    new_id = model.generate_id("genres")
    new_entry = {"id": new_id, "name": genre_name}
    model.add_entry("genres", new_entry)
    return(new_id)


def edit_genre(model: CSVDataModel, name: str, genre_id: int):
    model.edit_entry("genres", "id", genre_id, "name", name)


def delete_genre(model: CSVDataModel, genre_name):
    genre_id = model.get_genres_dict()[genre_name]
    model.delete_entry("genres", genre_id)


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


def manage_reading_table(model: CSVDataModel, mode: str):
    pass


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
