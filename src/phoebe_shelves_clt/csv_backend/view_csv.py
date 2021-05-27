""" Visualization of the database using the CSV backend

Visualize the backend database with options to filter, aggregate,
and transform the data into other formats using the CSV backend.

Todo:
    * Implement chart-based visualization using graphing modules
    * Implement aggregate statistics characterizations.
"""

import pandas as pd

from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.utils.data_model import CSVDataModel
from phoebe_shelves_clt import view

# Type Aliases
DataFrame = pd.DataFrame


def print_table(db: DataFrame, show_index: bool = False):
    """ Print a DataFrame as a formatted Markdown table

    Prints a DataFrame as a nicely-formatted table to the command-line. This
    function provides a wrapper around the "df.to_markdown()" function and some
    additional visual formatting.

    Args:
        db: DataFrame to print to the command-line.
        show_index: Flag to include the index of the DataFrame in the output.
    """
    print("\n" + db.to_markdown(tablefmt='grid', index=show_index) + "\n")


def reading_filter(model: CSVDataModel) -> DataFrame:
    """ Create a filtered user-friendly reading database.

    This method is controls the process flow to creating a filtered,
    user-friendly reading database. It prompts the user to select from
    the list of potential column filters and calls the appropriate filtering
    function.

    Args:
        model: The current CSVDataModel instance

    Returns:
        (DataFrame): The filtered, user-friendly reading database.
    """
    opts = ["Title", "Author", "Start", "Finish", "Read Time", "Rating"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author"}:
        return(view.options_filter("reading", selection,
                                   "csv", model=model))  # type: ignore
    elif selection in {"Start", "Finish"}:
        return(view.date_filter("reading", selection,
                                "csv", model=model))  # type: ignore
    else:  # Reading Time and Rating
        return(view.numeric_filter("reading", selection,
                                   "csv", model=model))  # type: ignore


def books_filter(model: CSVDataModel) -> DataFrame:
    """ Create a filtered user-friendly books database.

    This method is controls the process flow to creating a filtered,
    user-friendly books database. It prompts the user to select from
    the list of potential column filters and calls the appropriate filtering
    function.

    Args:
        model: The current CSVDataModel instance

    Returns:
        (DataFrame): The filtered, user-friendly books database.
    """
    opts = ["Title", "Author", "Times Read", "Rating", "Genre"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author", "Genre"}:
        return(view.options_filter("reading", selection,
                                   "csv", model=model))  # type: ignore
    else:  # Times Read, Rating
        return(view.numeric_filter("reading", selection,
                                   "csv", model=model))  # type: ignore


def main(db_select: str, mode: str, model: CSVDataModel):
    """ Main module function
    
    Main view module function to launch different workflows to visualize the
    different databases. Databases are first merged into a user-friendly
    presentation. The user is prompted multiple times to control the flow and
    options for the final visualization.

    Args:
        db_select: Which database to visualze.
        mode: Which visualization mode to utilize
        model: The current CSVDataModel instanc

    Todo:
        * Implement chart-based visualization using graphing modules
        * Implement aggregate statistics characterizations.
    """

    to_filter_prompt = "Would you like to filter/search the data first?"
    to_filter = inputs.confirm(to_filter_prompt)

    if db_select == "reading" and to_filter:
        db = reading_filter(model)
    elif db_select == "reading" and not to_filter:
        db = model.generate_main_reading()
    elif db_select == "books" and to_filter:
        db = books_filter(model)
    else:
        db = model.generate_main_books()
    
    if mode == "table":
        print_table(db.fillna(""))
    elif mode == "chart":
        # TODO: Implement chart visualization
        # ? TEMP TABLE: books_friendly/reading_friendly
        print("Chart visualization is not currently implemented.")
    elif mode == "stats":
        # TODO: Implement aggregate statistics
        # ? TEMP TABLE: books_friendly/reading_friendly
        print("Chart visualization is not currently implemented.")