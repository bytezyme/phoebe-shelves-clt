""" Visualization of the database using the CSV backend

Visualize the backend database with options to filter, aggregate,
and transform the data into other formats using the CSV backend.

Todo:
    * Implement chart-based visualization using graphing modules
    * Implement aggregate statistics characterizations.
    * Consolidate with the SQL backend view functions
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.utils.data_model import CSVDataModel

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


def numeric_filter(model: CSVDataModel, table: str, column: str) -> DataFrame:
    """ Filter the database using numeric data based on user input.

    Filters the databse using numeric columns provided by the user through
    interactive command-line prompts.

    Args:
        model: Current CSVDataModel instance.
        table: Name of the backend table to filter.
        column: Name of the column to use.

    Returns:
        filtered_data: Final filtered data that is ready for further use.
    """
    threshold_prompt = ("Would you like to filter based on a [1] ≤ threshold, "
                        "[2] ≥ threshold, [3] range, or [4] missing values?: ")
    threshold_mode = inputs.prompt_from_choices([1,2,3,4], threshold_prompt)
    lower_thresh_prompt = "What's the smallest value (inclusive)?: "
    upper_thresh_prompt = "What's the largest_value (inclusive)?: "

    if table == "reading":
        table_func = model.generate_main_reading
    else:
        table_func = model.generate_main_books

    if threshold_mode == 1:
        lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[lower_thresh])

    elif threshold_mode == 2:
        upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[upper_thresh])

    elif threshold_mode == 3:
        lower_thresh = inputs.prompt_for_pos_int(lower_thresh_prompt)
        upper_thresh = inputs.prompt_for_pos_int(upper_thresh_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[lower_thresh, upper_thresh])
    else:  # threshold_mode == 4
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode, thresholds=[])
    
    return(filtered_data)


def date_filter(model: CSVDataModel, table: str, column: str):
    """ Filter the database using date-based data based on user input.

    Filters the databse using date-based columns provided by the user through
    interactive command-line prompts.

    Args:
        model: Current CSVDataModel instance.
        table: Name of the backend table to filter.
        column: Name of the column to use.

    Returns:
        filtered_data: Final filtered data that is ready for further use.
    """
    threshold_prompt = ("Would you like to filter based on an [1] earliest date "
                        "(anytime after), [2] latest date (anytime before), "
                        "[3] range of dates, [4] specific year, or [5] "
                        "missing dates?: ")
    threshold_mode = inputs.prompt_from_choices([1,2,3,4,5], threshold_prompt)
    early_date_prompt = "What's the earliest date (inclusive)?: "
    late_date_prompt = "What's the latest date (inclusive)?: "
    year_prompt = "What year would you like to view?: "

    if table  == "reading":
        table_func = model.generate_main_reading
    else:
        table_func = model.generate_main_books

    if threshold_mode == 1:
        early_date = inputs.prompt_for_date(early_date_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[early_date])
    elif threshold_mode == 2:
        late_date = inputs.prompt_for_date(late_date_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[late_date])
    elif threshold_mode == 3:
        early_date = inputs.prompt_for_date(early_date_prompt)
        late_date = inputs.prompt_for_date(late_date_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[early_date, late_date])
    elif threshold_mode == 4:
        year = inputs.prompt_for_date(year_prompt)
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode,
                                   thresholds=[year])
    else:  # threshold_mode == 5
        filtered_data = table_func(to_filter=True, column=column,
                                   comp_type=threshold_mode, thresholds=[])

    return(filtered_data)


def options_filter(model: CSVDataModel, table: str, column: str):
    """ Filter the database by prompting the user select from a set of options.

    Filters the databse based on categorical-like columns where the value is
    selected by the user via an interactive command-line prompt. This prompt
    provides the user with a list of values to chose from rather than a
    prompt-search-and-verify approach.

    Args:
        model: Current CSVDataModel instance.
        table: Name of the backend table to filter.
        column: Name of the column to use.

    Returns:
        filtered_data: Final filtered data that is ready for further use.
    """

    if column == "Title":
        opts_dict = model.get_books_dict()
    elif column == "Author":
        opts_dict = model.get_authors_dict()
    else:
        opts_dict = model.get_genres_dict()

    # Select option
    id_list = []
    print(f"\nChoose from the {column.lower()} list below.")
    selection = inputs.prompt_from_choices(list(opts_dict.keys()))
    id_list.append(opts_dict[selection])

    # Filter the table
    if table == "books":
        return(model.generate_main_books(to_filter=True, column=column,
                                         id_list=id_list))
    else:
        return(model.generate_main_reading(to_filter=True, column=column,
                                           id_list=id_list))



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
        return(options_filter(model, "reading", selection))
    elif selection in {"Start", "Finish"}:
        return(date_filter(model, "reading", selection))
    else:  # Reading Time and Rating
        return(numeric_filter(model, "reading", selection))


def books_filter(model):
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
        return(options_filter(model, "books", selection))
    else:  # Times Read, Rating
        return(numeric_filter(model, "books", selection))


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