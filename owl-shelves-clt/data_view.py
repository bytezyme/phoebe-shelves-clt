import pandas as pd
import numpy as np

from utilities import prompt_for_options, prompt_for_column
from utilities import prompt_for_pos_integer, prompt_for_date


def print_db(db, db_type):
    """ Print database as formatted markdown table

    Inputs:
        db_path {string} -- Path to data directory

    Outputs:
        Prints formatted version of Pandas database to the terminal
    """
    if (db_type == 'books'):
        db = db.drop(['Author FN', 'Author MN', 'Author LN'], axis='columns')

    print('\n' + db.to_markdown(tablefmt='grid', index=False) + '\n')


def print_db_title(db, book_title):
    """ Prints a filtered database to only include entries for a certain book

    Inputs:
        db {DataFrame} -- Books or reading database as a pandas DataFrame
        book_title -- Title of book to filter on

    outputs:
        Prints formatted list (with index) of entires containing the book title
    """
    filtered_db = db[db['Title'] == book_title]
    print('\n' + filtered_db.to_markdown(tablefmt='grid') + '\n')


def request_filter():

    to_filter_prompt = ('Would you like to search/filter the '
                        'data first[Y/N]?: ')
    to_filter = input(to_filter_prompt)

    while to_filter not in {'Y', 'y', 'N', 'n'}:
        to_filter = input('Please choose [Y/N]: ')

    return(to_filter in {'Y', 'y'})

def books_filter(db):
    cols = db.columns
    cols_index = list(range(1, len(cols) + 1))
    cols_dict = dict(zip(cols_index, cols))
    col_select = prompt_for_column(cols_dict)
    
    # Categorical, so get unique values and select from them
    if col_select in {'Title', 'Author', 'Genre'}:
        print('Choose the option from the list below: \n')
        values = np.sort(db[col_select].unique())
        values_index = list(range(1, len(values) + 1))
        values_dict = dict(zip(values_index, values))
        values_select = prompt_for_column(values_dict)
        db = db[db[col_select] == values_select]
    else:
        threshold_prompt = ('Would you like to filter based on [1] ≥ threshold'
                            ', [2] ≤ threshold, or a [3] range?: ')
        threshold_opts = {1, 2, 3}
        threshold_mode = prompt_for_options(threshold_prompt, threshold_opts)

        if threshold_mode == 1:
            lower_thresh_prompt = 'What\'s the lower value (inclusive)?: '
            lower_thresh = prompt_for_pos_integer(lower_thresh_prompt)
            db = db[db[col_select] >= lower_thresh]
        elif threshold_mode == 2:
            upper_thresh_prompt = 'What\'s the upper value (inclusive?: '
            upper_thresh = prompt_for_pos_integer(upper_thresh_prompt)
            db = db[db[col_select] <= upper_thresh]
        else:
            lower_thresh_prompt = 'What\'s the lower value (inclusive)?: '
            lower_thresh = prompt_for_pos_integer(lower_thresh_prompt)
            upper_thresh_prompt = 'What\'s the upper value (inclusive?: '
            upper_thresh = prompt_for_pos_integer(upper_thresh_prompt)
            upper_filter = db[col_select] <= upper_thresh
            lower_filter = db[col_select] >= lower_thresh
            db = db[upper_filter & lower_filter]

    return(db)

def reading_filter(db):
    cols = db.columns
    cols_index = list(range(1, len(cols) + 1))
    cols_dict = dict(zip(cols_index, cols))
    col_select = prompt_for_column(cols_dict)
    
    # Categorical, so get unique values and select from them
    if col_select in {'Title'}:
        print('Choose the option from the list below: \n')
        values = np.sort(db[col_select].unique())
        values_index = list(range(1, len(values) + 1))
        values_dict = dict(zip(values_index, values))
        values_select = prompt_for_column(values_dict)
        db = db[db[col_select] == values_select]
    else:
        threshold_prompt = ('Would you like to filter based on [1] ≥ threshold'
                            ', [2] ≤ threshold, or a [3] range?: ')
        threshold_opts = {1, 2, 3}
        threshold_mode = prompt_for_options(threshold_prompt, threshold_opts)
        
        if col_select in {'Start', 'Finish'}:
            if threshold_mode == 1:
                lower_thresh_prompt = 'What\'s the lower value (inclusive)?: '
                lower_thresh = prompt_for_date(lower_thresh_prompt)
                db = db[db[col_select] >= lower_thresh]
            elif threshold_mode == 2:
                upper_thresh_prompt = 'What\'s the upper value (inclusive?: '
                upper_thresh = prompt_for_date(upper_thresh_prompt)
                db = db[db[col_select] <= upper_thresh]
            else:
                lower_thresh_prompt = 'What\'s the lower value (inclusive)?: '
                lower_thresh = prompt_for_date(lower_thresh_prompt)
                upper_thresh_prompt = 'What\'s the upper value (inclusive?: '
                upper_thresh = prompt_for_date(upper_thresh_prompt)
                upper_filter = db[col_select] <= upper_thresh
                lower_filter = db[col_select] >= lower_thresh
                db = db[upper_filter & lower_filter]
        else:
            if threshold_mode == 1:
                lower_thresh_prompt = 'What\'s the lower value (inclusive)?: '
                lower_thresh = prompt_for_pos_integer(lower_thresh_prompt)
                db = db[db[col_select] >= lower_thresh]
            elif threshold_mode == 2:
                upper_thresh_prompt = 'What\'s the upper value (inclusive?: '
                upper_thresh = prompt_for_pos_integer(upper_thresh_prompt)
                db = db[db[col_select] <= upper_thresh]
            else:
                lower_thresh_prompt = 'What\'s the lower value (inclusive)?: '
                lower_thresh = prompt_for_pos_integer(lower_thresh_prompt)
                upper_thresh_prompt = 'What\'s the upper value (inclusive?: '
                upper_thresh = prompt_for_pos_integer(upper_thresh_prompt)
                upper_filter = db[col_select] <= upper_thresh
                lower_filter = db[col_select] >= lower_thresh
                db = db[upper_filter & lower_filter]
    db['Start'] = pd.to_datetime(db['Start']).dt.date
    db['Finish'] = pd.to_datetime(db['Finish']).dt.date
    return(db)

def view_module(args, dir_path):

    # TODO: Have 1) walkthrough with no options or 2) direct with
    # TODO: Passed options

    # Step 1: Select which database to view
    db_select_prompt = ('Would you like to view the [1] books database or '
                        '[2] reading database?: ')
    db_select_opts = {1: 'books',
                      2: 'reading'}
    db_select = db_select_opts[prompt_for_options(db_select_prompt,
                                                  db_select_opts.keys())]
    db_path = dir_path + '/{}.csv'.format(db_select)
    db = pd.read_csv(db_path)

    # Step 2: Select View Mode
    view_mode_prompt = ('Would you like to [1] view as table, [2] visualize as'
                        ' a chart, or [3] calculate aggregate values?: ')
    view_mode_opts = {1, 2, 3}
    view_mode = prompt_for_options(view_mode_prompt, view_mode_opts)

    # Step 3: Filter data (if needed)
    to_filter = request_filter()
    if to_filter:
        if db_select == 'books':
            db = books_filter(db)
        else:
            db['Start'] = pd.to_datetime(db['Start'])
            db['Finish'] = pd.to_datetime(db['Finish'])
            db = reading_filter(db)

    # Step 4: Process into final form and visualize

    if view_mode == 1:
        print_db(db, db_select)
    elif view_mode == 2:
        pass
    else:
        # TODO: Implement aggregation selection
        pass