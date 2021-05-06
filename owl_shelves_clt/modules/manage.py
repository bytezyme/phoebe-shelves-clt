"""Utility functions for updating database entries"""

import pandas as pd
import numpy as np

from .view import print_db_title

from ..utils.input import prompt_from_enum_options, prompt_from_enum_dict
from ..utils.input import prompt_for_yes, prompt_for_date
from ..utils.input import gen_enum_dict_from_list

""" Common Functions """


def select_mode():
    """Requests user to select an update mode

    Outputs:
        update_mode {int} -- Indicates which of 3 update modes was selected
    """

    prompt = ('Do you want to [1] add a new entry, [2] edit a current '
              'entry, or [3] delete an entry?: ')
    options = {1, 2, 3}
    modes = {1: 'add', 2: 'edit', 3: 'delete'}
    return(modes[prompt_from_enum_options(prompt, options)])


def prompt_for_title(db, update_mode):
    """Request user to enter an acceptable book title

    Adding a book can accept any potential title. There are custom actions to
    deal with cases for the books and reading databases defined in the
    related functions. The other two update modes will only accept a title that
    already exists in a database. This is a specialized case because editing or
    removing a title requires it to already be present.

    Args:
        db {DataFrame} -- DataFrame of books or reading entries
        update_mode {Int} -- [1] Add, [2] Edit, or [3] Remove

    Outputs:
        book_title {string} -- Title of the book to use
    """

    book_title = book_title = input('Please enter the book title: ')

    if update_mode == 'add':
        return(book_title)
    else:
        while book_title not in db['Title'].values:
            book_title = input('Book doesn\'t exist. '
                               'Please reenter the title: ')
        return(book_title)


def prompt_for_property(prop_dict):
    """Consolidate general property prompt

    Requests user to select a property from the database to edit and the
    corresponding new value. The "title" is treated differently because edit
    mode enable the user to change a title to something not present

    Args:
        prop_dict {dict} -- Dictioanry mapping acceptable user inputs to a prop

    Outputs:
        new_value {string} -- String representation of the updated value
        prop_to_update {string} -- Name of the property to update
    """

    prop_to_update = prompt_from_enum_dict(prop_dict)
    update_prompt = 'What is the new {} value?: '.format(prop_to_update)

    # Use date parser if 'Start' or 'Finish
    if prop_to_update == 'Start' or prop_to_update == 'Finish':
        new_val = prompt_for_date(update_prompt)
    elif prop_to_update == 'Rating':
        new_val = prompt_for_rating(update_prompt)
    else:
        new_val = input(update_prompt)
    return((new_val, prop_to_update))


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
    rating = int(rating) if rating != '' else np.nan
    return(rating)


def prompt_for_author(books_db):
    """Prompt the user for author name details

    This function will prompt the user for details to fill out the full
    author name. It provides logic for searching the existing list of authors
    for a potential match (i.e., autofill).

    Inputs:
        books_db {Dataframe} -- Dataframe of exisiting books

    Outputs:
        author_fn {string} -- Author's first name
        author_mn {string} -- Author's middle name
        author_ln {string} -- Author's last name
    """

    author_ln = input('Author Last Name: ')
    # Return list of names that share the last name
    author_list = list(books_db.loc[books_db['Author LN'] == author_ln,
                                    'Author'].unique())

    # Two Options: Either there are options or there are none:
    if len(author_list) == 0:
        author_fn = input('Author First Name: ')
        author_mn = input('Author Middle Name (Optional): ')
    else:
        # Allow user to select from existing list or indicate new author
        print('The author may already exist. Select one of the following '
              'options to select an existing author or the last option to add '
              'a new author.')

        # Add New Author as options to author list
        author_list.append('New Author')

        author_dict = gen_enum_dict_from_list(author_list, zero_indexed=False)
        author_select = prompt_from_enum_dict(author_dict)

        # Two cases: select new author or not:
        if author_select == 'New Author':
            print('Provide the following information for a new author.')
            author_fn = input('Author First Name: ')
            author_mn = input('Author Middle Name (Optional): ')
        else:
            author_filter = books_db['Author'] == author_select
            author_index = books_db[author_filter].index[0]  # Need 1st index
            author_fn = books_db.loc[author_index, 'Author FN']
            author_mn = books_db.loc[author_index, 'Author MN']

    # Need to fix np.nan for author middle name is nothing is passed!
    if type(author_mn) != str:
        author_mn = ''

    return(author_fn, author_mn, author_ln)


def generate_full_author(author_fn, author_mn, author_ln):
    """Combines author names into a single column

    Args:
        author_fn {string} -- Author first name
        author_mn {string} -- Author middle name
        author_ln {string} -- Author last name

    Outputs:
        author {string} -- Combined author name (First, Middle, Last)
    """

    names = [name for name in [author_fn, author_mn, author_ln] if name != '']
    author = ' '.join(names)
    return(author)


def add_new_book(books_db, book_title):
    """Adds a new book to the book database

    Args:
        books_db {DataFrame} -- DataFrame representation of the books database
        book_title {string} -- Title of book to add to the database

    Outputs:
        books_db {DataFrame} -- DataFrame representation with new book
    """

    # Request the basic information
    print('Please enter the following optional information:')

    author_fn, author_mn, author_ln = prompt_for_author(books_db)
    author = generate_full_author(author_fn, author_mn, author_ln)

    while True:
        book_length = input('Book Length (Pages): ')

        if book_length == '':
            break
        else:
            try:
                book_length = int(book_length)
                break
            except ValueError:
                print('Please leave blank or enter an integer.\n')

    book_genre = input('Book Genre: ')

    new_book = {'Title': book_title,
                'Author FN': author_fn,
                'Author MN': author_mn,
                'Author LN': author_ln,
                'Author': author,
                'Length': book_length,
                'Genre': book_genre}

    # Append to database in memory
    return(books_db.append(new_book, ignore_index=True))


def edit_existing_book(books_db, book_title):
    """Edits an exisiting book in the database

    Args:
        books_db {DataFrame} -- DataFrame representation of the books database
        book_title {string} -- Title of book to edit

    Outputs:
        books_db {DataFrame} -- DataFrame representation with edited properties
    """

    print('Which property would you like to edit?')

    prop_dict = {1: 'Title',
                 2: 'Author FN',
                 3: 'Author MN',
                 4: 'Author LN',
                 5: 'Length',
                 6: 'Rating',
                 7: 'Genre'}

    new_value, prop_to_update = prompt_for_property(prop_dict)

    # Change type as needed:
    if prop_to_update == 'Length':
        new_value = int(new_value)
    elif prop_to_update == 'Rating':
        new_value = float(new_value)

    # Update Value
    books_db.loc[books_db['Title'] == book_title, prop_to_update] = new_value

    # Need special case to update combined author if needed
    if prop_to_update in ['Author FN', 'Author MN', 'Author LN']:
        author_fn = books_db.loc[books_db['Title'] == book_title,
                                 'Author FN'].values[0]
        author_mn = books_db.loc[books_db['Title'] == book_title,
                                 'Author MN'].values[0]

        # Fix if missing value
        author_fn = '' if pd.isna(author_fn) else author_fn
        author_mn = '' if pd.isna(author_mn) else author_mn

        author_ln = books_db.loc[books_db['Title'] == book_title,
                                 'Author LN'].values[0]
        books_db.loc[books_db['Title'] == book_title, 'Author'] = \
            generate_full_author(author_fn, author_mn, author_ln)

    return(books_db)


def remove_existing_book(books_db, book_title):
    """Removes an existing book from the database

    Args:
        books_db {DataFrame} -- DataFrame representation of the books database
        book_title {string} -- Title of book to remove

    Outputs:
        books_db {DataFrame} -- DataFrame with book_title removed
    """

    return(books_db.drop(books_db[books_db['Title'] == book_title].index))


def update_book_db(update_mode, db_directory):
    """Main function to update book database

    Args:
        args {object} -- object containing command line arguments
        db_directory {string} -- Path to the data directory

    Outputs:
        Saves an updated book database as a csv to the disk
    """

    # Read in saved database
    db_path = db_directory + '/books.csv'
    books_db = pd.read_csv(db_path)

    # Select Mode
    book_title = prompt_for_title(books_db, update_mode)

    if update_mode == 'add':

        # Need to check case where book actually already exists
        if book_title in books_db['Title'].values:
            print('{} already exists in the database.'.format(book_title))
            print('The database only supports one entry per title. Adding '
                  'an entry will result in overwriting the previous data.')
            switch_prompt = ('Would you like to edit the existing entry '
                             'instead [Y/N]?: ')
            switch_to_edit = prompt_for_yes(switch_prompt)

            if switch_to_edit:
                books_db = edit_existing_book(books_db, book_title)
            else:
                books_db.drop(books_db[books_db['Title'] == book_title].index,
                              inplace=True)
                books_db = add_new_book(books_db, book_title)
        else:
            books_db = add_new_book(books_db, book_title)
    elif update_mode == 'edit':
        books_db = edit_existing_book(books_db, book_title)
    else:
        books_db = remove_existing_book(books_db, book_title)

    # Sort books by author last name
    books_db = books_db.sort_values(by=['Author LN', 'Title'],
                                    ignore_index=True)
    books_db.to_csv(db_path, index=False)


def update_reading_time(start, finish):
    """Calculate reading time using start and finish dates

    Args:
        start {datetime} -- Start date
        finish {datetime} -- Finish date

    Outputs:
        Reading time (in days) or pd.NaT is missing a start/finish date
    """

    if pd.isnull(start) or pd.isnull(finish):
        return(pd.NaT)
    else:
        return((finish - start).days + 1)


def update_reading_count(reading_db, books_db, book_title):
    """ pdate reading count in books.csv from reading entries

    Args:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        books_db {DataFrame} -- Pandas DataFrame of the books database
        book_title -- Title of book to use for the entry

    Outputs:
        books_db {DataFrame} -- Updated books DataFrame
    """

    # Calculate read count
    title_filter = reading_db['Title'] == book_title
    finish_filter = reading_db['Finish'].notna()

    read_cnt = int(reading_db.loc[title_filter & finish_filter].shape[0])

    books_db.loc[books_db['Title'] == book_title, 'Times Read'] = read_cnt
    return(books_db)


def update_book_rating(reading_db, books_db, book_title):
    """Propogates average rating to the book database

    Args:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        books_db {DataFrame} -- Pandas DataFrame of the books database
        book_title -- Title of book to use for the entry

    Outputs:
        books_db {DataFrame} -- Updated books DataFrame
    """

    # Filter and Make sure we create numerics for rating
    title_filter = reading_db['Title'] == book_title
    avg_rating = reading_db.loc[title_filter, 'Rating'].mean()

    # Only update book database if we can calculate an average
    if pd.notna(avg_rating):
        avg_rating = round(avg_rating, 1)

    books_db.loc[books_db['Title'] == book_title, 'Rating'] = avg_rating
    return(books_db)


def propogate_to_book_db(reading_db, dir_path, book_title, mode):
    """Propogate reading database updates to the books database

    Args:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Book title
        mode {string} -- Add/Edit/Remove mode indicator

    Outputs:
        Saves the updated books database as a csv to the dir_path
    """

    books_db_path = dir_path + '/books.csv'
    books_db = pd.read_csv(books_db_path)
    book_exists = book_title in books_db['Title'].values

    if mode == 'remove' and not book_exists:
        print('Book doesn\'t exist in the books directory. No updates needed')
    else:
        # Add book first if it doesn't exist yet
        if not book_exists:
            print('Cannot find {} in the books database.'.format(book_title))
            print('Let\'s make a new entry...')
            books_db = add_new_book(books_db, book_title)

        books_db = update_reading_count(reading_db, books_db, book_title)
        books_db = update_book_rating(reading_db, books_db, book_title)
        books_db = books_db.sort_values(by=['Author LN', 'Title'],
                                        ignore_index=True)
        books_db.to_csv(books_db_path, index=False)


def add_reading_entry(reading_db, dir_path, book_title):
    """Adds a new reading entry for a book

    Args:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Title of book to use for the entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with new reading entry
        Saves an updated books database based on the updates
    """

    print('Please enter the following optional information for a new entry:')

    # Get optional information

    start_date = prompt_for_date('Start Date: ')
    finish_date = prompt_for_date('End Date: ')
    rating = prompt_for_rating('Rating (1-5): ')

    # Create temporary entry object
    new_entry_dict = {'Title': book_title,
                      'Start': start_date,
                      'Finish': finish_date,
                      'Reading Time': update_reading_time(start_date,
                                                          finish_date),
                      'Rating': rating}

    # Update reading database
    reading_db = reading_db.append(new_entry_dict, ignore_index=True)

    # Propogate updates to books database
    propogate_to_book_db(reading_db, dir_path, book_title, 'add')

    return(reading_db)


def edit_reading_entry(reading_db, dir_path, book_title):
    """Edits properties of an existing reading entry

    Args:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Title of book to filter for the reading entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with updated entriy
        Saves an updated books database based on the updates
    """

    filtered_db = reading_db[reading_db['Title'] == book_title]
    print_db_title(reading_db, book_title)

    edit_prompt = 'Which entry (index) would you like to edit?: '
    edit_options = filtered_db.index
    index_to_edit = prompt_from_enum_options(edit_prompt, edit_options)

    print('Which property would you like to edit?')

    prop_dict = {1: 'Title',
                 2: 'Start',
                 3: 'Finish',
                 4: 'Rating',
                 }

    new_value, prop_to_update = prompt_for_property(prop_dict)

    reading_db.loc[index_to_edit, prop_to_update] = new_value

    # Do autoupdate of reading time
    new_time = update_reading_time(reading_db.loc[index_to_edit, 'Start'],
                                   reading_db.loc[index_to_edit, 'Finish'])
    reading_db.loc[index_to_edit, 'Reading Time'] = new_time

    # Propogate changes to books database
    propogate_to_book_db(reading_db, dir_path, book_title, 'edit')

    return(reading_db)


def remove_reading_entry(reading_db, dir_path, book_title):
    """Removes a reading entry

    Args:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Title of book to filter for the reading entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with updated entriy
        Saves an updated books database based on the updates
    """

    filtered_db = reading_db[reading_db['Title'] == book_title]
    print_db_title(reading_db, book_title)

    remove_prompt = 'Which entry (index) would you like to remove?: '
    remove_options = filtered_db.index
    index_to_remove = prompt_from_enum_options(remove_prompt, remove_options)
    reading_db = reading_db.drop(index_to_remove)

    # Propogation to book database
    propogate_to_book_db(reading_db, dir_path, book_title, 'remove')

    return(reading_db)


def update_reading_db(update_mode, dir_path):
    """Main function to update book database

    Args:
        args {object} -- object containing command line arguments
        dir_path {string} -- Path to the data directory

    Outputs:
        Saves an updated reading database as a csv to the disk
    """

    # Read in reading database
    reading_db_path = dir_path + '/reading.csv'
    reading_db = pd.read_csv(reading_db_path)

    # Requires additional formatting for dates
    reading_db['Start'] = pd.to_datetime(reading_db['Start']).dt.date
    reading_db['Finish'] = pd.to_datetime(reading_db['Finish']).dt.date

    # Select Mode
    # update_mode = args.mode if args.mode is not None else select_mode()
    # print('Entering {} mode...'.format(update_mode))

    title = prompt_for_title(reading_db, update_mode)

    if update_mode == 'add':
        if title in reading_db['Title'].values:
            print('An entry for {} already exists.'.format(title))
            switch_prompt = 'Would you like to edit an entry instead [Y/N]?: '
            switch_to_edit = prompt_for_yes(switch_prompt)

            if switch_to_edit:
                reading_db = edit_reading_entry(reading_db, dir_path, title)
            else:
                reading_db = add_reading_entry(reading_db, dir_path, title)
        else:
            reading_db = add_reading_entry(reading_db, dir_path, title)
    elif update_mode == 'edit':
        reading_db = edit_reading_entry(reading_db, dir_path, title)
    else:
        reading_db = remove_reading_entry(reading_db, dir_path, title)

    reading_db.sort_values(['Finish', 'Start'], na_position='last',
                           inplace=True)
    reading_db.to_csv(reading_db_path, index=False)


def management_module(database, mode, dir_path):
    if database == 'books':
        update_book_db(mode, dir_path)
    else:
        update_reading_db(mode, dir_path)
