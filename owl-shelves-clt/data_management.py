import os
import pandas as pd
import numpy as np
import dateutil

from data_view import print_db, print_filtered_db

""" Common Functions """


def select_mode():
    """ Requests user to select an update mode

    Outputs:
        update_mode {int} -- Indicates which of 3 update modes was selected
    """

    input_prompt = ('Do you want to [1] add a new entry, [2] edit a current '
                    'entry, or [3] remove an entry?: ')
    valid_options = {1, 2, 3}
    return(prompt_for_options(input_prompt, valid_options))


def prompt_for_options(input_prompt, valid_options):
    """ Function to prompt and validate user input for enumerated options

    This function provides the general structure for prompting a user to
    select from a set of enumerated options using the input() method. This
    ensures the input is 1) a valid integer and 2) within the presented list
    of options

    Inputs:
        input_prompt {string} -- Input prompt string
        valid_options {set} -- Set of valid input options

    Outputs:
        selection {int} -- Selected option from user input
    """

    while True:
        try:
            selection = int(input(input_prompt))
            if selection not in valid_options:
                raise ValueError
            return(selection)
        except ValueError:
            print('Please enter one of the valid options.\n')


def prompt_for_title(db, update_mode):
    """ Request user to enter an acceptable book title

    Adding a book can accept any potential title. There are custom actions to
    deal with cases for the books and reading databases defined in the
    related functions. The other two update modes will only accept a title that
    already exists in a database. This is a specialized case because editing or
    removing a title requires it to already be present.

    Inputs:
        db {DataFrame} -- DataFrame of books or reading entries
        update_mode {Int} -- [1] Add, [2] Edit, or [3] Remove

    Outputs:
        book_title {string} -- Title of the book to use

    """

    book_title = book_title = input('Please enter the book title: ')

    if update_mode == 1:
        return(book_title)
    else:
        while book_title not in db['Title'].values:
            book_title = input('Book doesn\'t exist. '
                               'Please reenter the title: ')
        return(book_title)


def prompt_for_property(prop_dict):
    """ Consolidate general property prompt

    Requests user to select a property from the database to edit and the
    corresponding new value. The "title" is treated differently because edit
    mode enable the user to change a title to something not present

    Inputs:
        prop_dict {dict} -- Dictioanry mapping acceptable user inputs to a prop

    Outputs:
        new_value {string} -- String representation of the updated value
        prop_to_update {string} -- Name of the property to update
    """

    # Request Prompt
    prop_update_prompt = ['[{}] {}'.format(key, value)
                          for key, value
                          in prop_dict.items()]
    prop_update_prompt = '\n'.join(prop_update_prompt) + '\nSelection: '

    # Ensure request is a valid property choice

    prop_to_update = prompt_for_options(prop_update_prompt,
                                        set(prop_dict.keys()))

    prop_to_update = prop_dict[prop_to_update]

    # Get new value
    new_value = input('What is the new {} value?: '.format(prop_to_update))
    return((new_value, prop_to_update))


def prompt_for_date(property_name):
    """ General date prompt with error catching

    Inputs:
        property_name {string} -- Name of the property to prompt for

    Outputs:
        date {Datetime} -- Datetime object with only the date
    """

    date = ''

    while True:
        try:
            date = pd.to_datetime(input('{}: '.format(property_name))).date()
        except dateutil.parser._parser.ParserError:
            print('Cannot parse the input to a date. Please try again.')
            continue
        break

    return(date)


""" Database Creation """


def create_database(db_path):
    """ Create the appropriate database at the given path

    Inputs:
        db_path {string} -- Indicates which database and its path

    Outputs:
        Saves an empty version of the appropriate database at db_path
    """

    if 'books.csv' in db_path:
        cols = ['Title', 'Author', 'Author FN', 'Author MN',
                'Author LN', 'Length', 'Times Read', 'Rating', 'Genre']
        name = 'books'
    else:
        cols = ['Title', 'Start', 'Finish', 'Reading Time', 'Rating']
        name = 'reading'

    pd.DataFrame(columns=cols).to_csv(db_path, index=False)
    print('Successfully created the {} database!'.format(name))


def create_databases(force_overwrite, data_directory):
    """ Creates initial book and reading date csv files if not present

    Inputs:
        force_overwrite {bool} -- Indicates to overwrite existing databases
        data_directory {string} -- Path to the data directory

    Outputs:
        Prints out status of the process
        Writes empty reading and book databases to the data_directory
    """

    print('Checking for data...')
    books_db_path = data_directory + '/books.csv'
    reading_db_path = data_directory + '/reading.csv'

    books_db_exists = os.path.isfile(books_db_path)
    reading_db_exists = os.path.isfile(reading_db_path)

    # Check for books.csv

    if books_db_exists and not force_overwrite:
        print('Book database already created. '
              'Pass -f to force overwrite the current database.')
    elif books_db_exists and force_overwrite:
        print('Overwriting existing books database...')
        create_database(books_db_path)
    else:
        print('Creating book database...')
        create_database(books_db_path)

    # Check for reading.csv
    if reading_db_exists and not force_overwrite:
        print('Reading event database already created. '
              'Pass -f to force overwrite the current database.')
    elif reading_db_exists and force_overwrite:
        print('Overwriting reading database...')
        create_database(reading_db_path)
    else:
        print('Creating reading database...')
        create_database(reading_db_path)


""" Books database updates """


def generate_full_author(author_fn, author_mn, author_ln):
    """ Combines author names into a single column

    Inputs:
        author_fn {string} -- Author first name
        author_mn {string} -- Author middle name
        author_ln {string} -- Author last name

    Outputs
        author {string} -- Combined author name (First, Middle, Last)
    """

    if author_mn == '':
        author = ' '.join([author_fn, author_ln])
    else:
        author = ' '.join([author_fn, author_mn, author_ln])
    return(author)


def prompt_for_author(books_db):
    """ Prompt the user for author name details

    This function will prompt the user for details to fill out the full
    author name. It provides logic for searching the existing list of authors
    for a potential match (i.e., autofill).

    Inputs:
        books_db {Dataframe} -- Dataframe of exisiting books

    Returns:
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
        prompt_strings = ['[{}] {}'.format(option + 1, name)
                          for option, name
                          in enumerate(author_list)]
        new_author_index = len(author_list) + 1  # Last index for prompt
        prompt_strings.append('[{}] New Author'.format(new_author_index))
        select_prompt = '\n'.join(prompt_strings) + '\nSelection: '
        author_options = set(range(1, new_author_index+1))

        # Only accept a correct answer
        author_select = prompt_for_options(select_prompt, author_options)

        # Two cases: select new author or not:
        if author_select == new_author_index:
            print('Provide the following information for a new author.')
            author_fn = input('Author First Name: ')
            author_mn = input('Author Middle Name (Optional): ')
        else:
            author_filter = books_db['Author'] == author_list[author_select-1]
            author_index = books_db[author_filter].index[0]  # Need 1st index
            author_fn = books_db.loc[author_index, 'Author FN']
            author_mn = books_db.loc[author_index, 'Author MN']

    # Need to fix np.nan for author middle name is nothing is passed!
    if type(author_mn) != str:
        author_mn = ''

    return(author_fn, author_mn, author_ln)


def add_new_book(books_db, book_title):
    """ Adds a new book to the book database

    Inputs:
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
    """ Edits an exisiting book in the database

    Inputs:
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

        # Fix if no middle name!
        author_mn = '' if pd.isna(author_mn) else author_mn

        author_ln = books_db.loc[books_db['Title'] == book_title,
                                 'Author LN'].values[0]
        books_db.loc[books_db['Title'] == book_title, 'Author'] = \
            generate_full_author(author_fn, author_mn, author_ln)

    return(books_db)


def remove_existing_book(books_db, book_title):
    """ Removes an existing book from the database

    Inputs:
        books_db {DataFrame} -- DataFrame representation of the books database
        book_title {string} -- Title of book to remove

    Outputs:
        books_db {DataFrame} -- DataFrame with book_title removed
    """

    return(books_db.drop(books_db[books_db['Title'] == book_title].index))


def update_book_db(db_directory):
    """ Main function to update book database

    Inputs:
        db_directory {string} -- Path to the data directory

    Outputs:
        Saves an updated book database as a csv to the disk
    """

    # Read in saved database
    db_path = db_directory + '/' + 'books.csv'
    books_db = pd.read_csv(db_path)

    # Print database for easy access
    print_db(db_path)

    update_mode = select_mode()
    book_title = prompt_for_title(books_db, update_mode)

    if update_mode == 1:

        # Need to check case where book actually already exists
        if book_title in books_db['Title'].values:
            print('{} already exists in the database.'.format(book_title))
            mode_prompt = ('Would you like to [1] edit the existing entry '
                           'or [2] overwrite the data?: ')
            mode_options = {1, 2}
            switch_mode = prompt_for_options(mode_prompt, mode_options)

            if int(switch_mode) == 1:
                books_db = edit_existing_book(books_db, book_title)
            else:
                books_db.drop(books_db[books_db['Title'] == book_title].index,
                              inplace=True)
                books_db = add_new_book(books_db, book_title)
        else:
            books_db = add_new_book(books_db, book_title)
    elif update_mode == 2:
        books_db = edit_existing_book(books_db, book_title)
    else:
        books_db = remove_existing_book(books_db, book_title)

    # Sort books by author last name
    books_db = books_db.sort_values(by=['Author LN', 'Title'],
                                    ignore_index=True)
    books_db.to_csv(db_path, index=False)


""" Reading database updates """


def update_reading_time(start, finish):
    """ Calculate reading time using start and finish dates

    Inputs:
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
    """ Update reading count in books.csv from reading entries

    Inputs:
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
    """ Propogates average rating to the book database

    Inputs:
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
    """ Propogate reading database updates to the books database

    Inputs:
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

    # TODO: Potentially explore cleaner implementation...

    if book_exists:
        books_db = update_reading_count(reading_db, books_db, book_title)
        books_db = update_book_rating(reading_db, books_db, book_title)
        books_db = books_db.sort_values(by=['Author LN', 'Title'],
                                        ignore_index=True)
        books_db.to_csv(books_db_path, index=False)
    elif mode == 'remove' and not book_exists:
        print('Book doesn\'t exist in the books directory. No updates needed')
    else:
        print('Cannot find {} in the books database.'.format(book_title))
        print('Let\'s make a new entry...')
        books_db = add_new_book(books_db, book_title)
        books_db = update_reading_count(reading_db, books_db, book_title)
        books_db = update_book_rating(reading_db, books_db, book_title)
        books_db = books_db.sort_values(by=['Author LN', 'Title'],
                                        ignore_index=True)
        books_db.to_csv(books_db_path, index=False)


def add_reading_entry(reading_db, dir_path, book_title):
    """ Adds a new reading entry for a book

    Inputs:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Title of book to use for the entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with new reading entry
        Saves an updated books database based on the updates
    """

    print('Please enter the following optional information for a new entry:')

    # Get optional information

    start_date = prompt_for_date('Start Date')
    finish_date = prompt_for_date('End Date')
    rating = input('Rating (1-5): ')

    while rating not in {'', '1', '2', '3', '4', '5'}:
        rating = input('Choose an integer between 1 and 5 or leave blank: ')

    # Format rating
    rating = int(rating) if rating != '' else np.nan

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
    """ Edits properties of an existing reading entry

    Inputs:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Title of book to filter for the reading entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with updated entriy
        Saves an updated books database based on the updates
    """

    filtered_db = reading_db[reading_db['Title'] == book_title]
    print_filtered_db(reading_db, book_title)

    edit_prompt = 'Which entry (index) would you like to edit?: '
    edit_options = filtered_db.index
    index_to_edit = prompt_for_options(edit_prompt, edit_options)

    print('Which property would you like to edit?')

    prop_dict = {1: 'Title',
                 2: 'Start',
                 3: 'Finish',
                 4: 'Rating',
                 }

    new_value, prop_to_update = prompt_for_property(prop_dict)

    # Correctly format the information
    if prop_to_update == 'Start' or prop_to_update == 'Finish':
        while True:
            try:
                new_value = pd.to_datetime(new_value).date()
            except dateutil.parser._parser.ParserError:
                print('Cannot parse the input to a date. Please try again.')
                new_value = input('What is the new date?: ')
                continue
            break
    elif prop_to_update == 'Rating':
        new_value = int(new_value) if new_value != '' else np.nan

    reading_db.loc[index_to_edit, prop_to_update] = new_value

    # Do autoupdate of reading time
    new_time = update_reading_time(reading_db.loc[index_to_edit, 'Start'],
                                   reading_db.loc[index_to_edit, 'Finish'])
    reading_db.loc[index_to_edit, 'Reading Time'] = new_time

    # Propogate changes to books database
    propogate_to_book_db(reading_db, dir_path, book_title, 'edit')

    return(reading_db)


def remove_reading_entry(reading_db, dir_path, book_title):
    """ Removes a reading entry

    Inputs:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        dir_path {string} -- Path to directory containing the database csv's
        book_title {string} -- Title of book to filter for the reading entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with updated entriy
        Saves an updated books database based on the updates
    """

    filtered_db = reading_db[reading_db['Title'] == book_title]
    print_filtered_db(reading_db, book_title)

    remove_prompt = 'Which entry (index) would you like to remove?: '
    remove_options = filtered_db.index
    index_to_remove = prompt_for_options(remove_prompt, remove_options)
    reading_db = reading_db.drop(index_to_remove)

    # Propogation to book database
    propogate_to_book_db(reading_db, dir_path, book_title, 'edit')

    return(reading_db)


def update_reading_db(dir_path):
    """ Main function to update book database

    Inputs:
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

    # Print full database for ease of viewing
    print_db(reading_db_path)

    update_mode = select_mode()

    title = prompt_for_title(reading_db, update_mode)

    if update_mode == 1:
        if title in reading_db['Title'].values:
            print('An entry for {} already exists.'.format(title))
            switch_prompt = 'Would you like to edit an entry instead [Y/N]?: '
            switch_to_edit = input(switch_prompt)

            # First restrict to acceptable inputs
            while switch_to_edit not in {'Y', 'y', 'N', 'n'}:
                switch_to_edit = input('Please choose [Y/N]: ')

            if switch_to_edit in {'Y', 'y'}:
                reading_db = edit_reading_entry(reading_db, dir_path, title)
            elif switch_to_edit in {'N', 'n'}:
                reading_db = add_reading_entry(reading_db, dir_path, title)
        else:
            reading_db = add_reading_entry(reading_db, dir_path, title)
    elif update_mode == 2:
        reading_db = edit_reading_entry(reading_db, dir_path, title)
    else:
        reading_db = remove_reading_entry(reading_db, dir_path, title)

    reading_db.sort_values(['Finish', 'Start'], na_position='last',
                           inplace=True)
    reading_db.to_csv(reading_db_path, index=False)
