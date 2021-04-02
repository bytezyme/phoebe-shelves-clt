import pandas as pd
import numpy as np

from input_utils import prompt_from_enum_dict, prompt_from_enum_options
from input_utils import prompt_for_pos_int, prompt_for_date, prompt_for_yes


def print_db(db, db_type):
    """Print database as formatted markdown table

    Args:
        db_path {string} -- Path to data directory

    Outputs:
        Prints formatted version of Pandas database to the terminal
    """

    if (db_type == 'books'):
        db = db.drop(['Author FN', 'Author MN', 'Author LN'], axis='columns')

    print('\n' + db.to_markdown(tablefmt='grid', index=False) + '\n')


def print_db_title(db, book_title):
    """Prints a filtered database to only include entries for a certain book

    Args:
        db {DataFrame} -- Books or reading database as a pandas DataFrame
        book_title -- Title of book to filter on

    Outputs:
        Prints formatted list (with index) of entires containing the book title
    """

    filtered_db = db[db['Title'] == book_title]
    print('\n' + filtered_db.to_markdown(tablefmt='grid') + '\n')


def numerical_threshold_filter(db, col_select):
    """Use numerical thresholds to filter the database

    Args:
        db {DataFrame} -- Books or reading database as a pandas DataFrame
        col_select {string} -- Column to filter on

    Outputs:
        db {DataFrame} -- Database filtered based on user-given thresholds
    """

    threshold_prompt = ('Would you like to filter based on [1] ≥ threshold'
                        ', [2] ≤ threshold, or a [3] range?: ')
    threshold_opts = {1, 2, 3}
    threshold_mode = prompt_from_enum_options(threshold_prompt, threshold_opts)

    lower_thresh_prompt = 'What\'s the smallest value (inclusive)?: '
    upper_thresh_prompt = 'What\'s the largest value (inclusive)?: '

    is_date = col_select in {'Start', 'Finish'}

    prompt_function = prompt_for_date if is_date else prompt_for_pos_int

    if threshold_mode == 1:
        lower_thresh = prompt_function(lower_thresh_prompt)
        db = db[db[col_select] >= lower_thresh]
    elif threshold_mode == 2:
        upper_thresh = prompt_function(upper_thresh_prompt)
        db = db[db[col_select] <= upper_thresh]
    else:
        lower_thresh = prompt_function(lower_thresh_prompt)
        upper_thresh = prompt_function(upper_thresh_prompt)
        upper_filter = db[col_select] <= upper_thresh
        lower_filter = db[col_select] >= lower_thresh
        db = db[upper_filter & lower_filter]

    return(db)


def books_filter(db):
    cols = db.columns.drop(['Author FN', 'Author MN', 'Author LN'])
    cols_index = list(range(1, len(cols) + 1))
    cols_dict = dict(zip(cols_index, cols))
    col_select = prompt_from_enum_dict(cols_dict)

    numeric_cols = {'Length', 'Times Read', 'Rating'}
    
    # Categorical, so get unique values and select from them
    if col_select not in numeric_cols:
        print('Choose the option from the list below: \n')

        # Special Sort for Authors (present full author sort by last name)
        if col_select == 'Author':
            temp_df = db[['Author', 'Author LN']].sort_values(by=['Author LN'])
            values = temp_df['Author'].unique()
        else:
            values = db[col_select].sort_values().unique()
        
        values_index = list(range(1, len(values) + 1))
        values_dict = dict(zip(values_index, values))
        values_select = prompt_from_enum_dict(values_dict)

        if pd.isna(values_select):
            db = db[pd.isna(db[col_select])]
        else:
            db = db[db[col_select] == values_select]
    else:  # Numerical category, so use threshold filter
        db = numerical_threshold_filter(db, col_select)
    return(db)


def reading_filter(db):
    cols = db.columns
    cols_index = list(range(1, len(cols) + 1))
    cols_dict = dict(zip(cols_index, cols))
    col_select = prompt_from_enum_dict(cols_dict)
    
    # Categorical, so get unique values and select from them
    if col_select in {'Title'}:
        print('Choose the option from the list below: \n')
        values = db[col_select].sort_values().unique()
        values_index = list(range(1, len(values) + 1))
        values_dict = dict(zip(values_index, values))
        values_select = prompt_from_enum_dict(values_dict)
        db = db[db[col_select] == values_select]
    else:
        db = numerical_threshold_filter(db, col_select)

    db['Start'] = pd.to_datetime(db['Start']).dt.date
    db['Finish'] = pd.to_datetime(db['Finish']).dt.date
    return(db)


def view_module(args, dir_path):

    # TODO: Have 1) walkthrough with no options or 2) direct with
    # TODO: Passed options

    # Step 1: Select which database to view
    db_select_prompt = ('Would you like to view the [1] books database or '
                        '[2] reading database?: ')
    db_select_opts = {1, 2}
    db_select = prompt_from_enum_options(db_select_prompt, db_select_opts)
    db_select = 'books' if db_select == 1 else 'reading'
    db_path = dir_path + '/{}.csv'.format(db_select)
    db = pd.read_csv(db_path)

    # Step 2: Select View Mode
    view_mode_prompt = ('Would you like to [1] view as table, [2] visualize as'
                        ' a chart, or [3] calculate aggregate values?: ')
    view_mode_opts = {1, 2, 3}
    view_mode = prompt_from_enum_options(view_mode_prompt, view_mode_opts)

    # Step 3: Filter data (if needed)
    to_filter_prompt = 'Would you like to search/filter the data first[Y/N]?: '
    to_filter = prompt_for_yes(to_filter_prompt)

    if to_filter:
        if db_select == 'books':
            db = books_filter(db)
        else:
            db['Start'] = pd.to_datetime(db['Start']).dt.date
            db['Finish'] = pd.to_datetime(db['Finish']).dt.date
            db = reading_filter(db)

    # Step 4: Process into final form and visualize

    if view_mode == 1:
        print_db(db, db_select)
    elif view_mode == 2:
        pass
    else:
        # TODO: Implement aggregation selection
        pass