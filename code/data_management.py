import pandas as pd
import os

from data_view import print_db, print_filtered_db

### Common Functions

def select_mode():
    """ Requests user to select an update mode

    Outputs:
        update_mode {int} -- Indicates which of 3 update modes was selected
    """
    update_mode = int(input('Do you want to [1] add a new entry, [2] edit a'
                            'current entry, or [3] remove an entry?: '))

    while update_mode not in [1,2,3]:
        print('{} is not a valid option'.format(update_mode))
        update_mode = int(input('Please select [1] add a new entry, [2] edit '
                                'a current entry, or [3] remove an entry?: '))
    return(update_mode)

def prompt_for_title(db, update_mode):
    """ Request user to enter an acceptable book title

    Adding a book can accept any potential title. There are custom actions to
    deal with cases for the books and reading databases defined in the
    related functions. The other two update modes will only accept a title that
    already exists in a database.

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

### Database Creation

def create_books_db(db_path):
    """ Create an empty books database

    Inputs:
        db_path {string} -- Path to save the database file to

    Outputs:
        Saves an empty DataFrame with columns to disk
        Prints confirmation to the terminal
    """

    book_db_cols = ['Title', 'Author', 'Author FN', 'Author MN',
                    'Author LN', 'Length', 'Times Read', 'Genre']
    pd.DataFrame(columns=book_db_cols).to_csv(db_path, index=False)
    print('Successfully created book database.')

def create_reading_db(db_path):
    """ Create an empty reading database

    Inputs:
        db_path {string} -- Path to save the database file to

    Outputs:
        Saves an empty DataFrame with columns to disk
        Prints confirmation to the terminal
    """

    book_db_cols = ['Title', 'Start', 'Finish', 'Reading Time']
    pd.DataFrame(columns=book_db_cols).to_csv(db_path, index=False)
    print('Successfully created reading event database.')

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
    books_db_path = data_directory + '/' + 'books.csv'
    reading_db_path = data_directory + '/' + 'reading.csv'

    books_db_exists = os.path.isfile(books_db_path)
    reading_db_exists = os.path.isfile(reading_db_path)

    # Check for books.csv
    if books_db_exists and not force_overwrite:
        print('Book database already created. '
              'Pass -f to force overwrite the current database.')
    elif books_db_exists and force_overwrite:
        print('Overwriting existing books database...')
        create_books_db(books_db_path)
    else:
        print('Creating book database...')
        create_books_db(books_db_path)

    # Check for reading.csv
    if reading_db_exists and not force_overwrite:
        print('Reading event database already created. '
              'Pass -f to force overwrite the current database.')
    elif reading_db_exists and force_overwrite:
        print('Overwriting reading database...')
        create_reading_db(reading_db_path)
    else:
        print('Creating reading database...')
        create_reading_db(reading_db_path)

### Book Database Updates

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

def add_new_book(books_db, book_title):
    """ Adds a new book to the book database

    Inputs:
        books_db {DataFrame} -- DataFrame representation of the books database
        book_title {string} -- Title of book to add to the database

    Outputs:
        books_db {DataFrame} -- DataFrame representation with new book
    """

    # Request individual column information
    print('Please enter the following optional information:')
    new_book = {'Title': book_title,
                'Author FN': input('Author First Name: '),
                'Author MN': input('Author Middle Name: '),
                'Author LN': input('Author Last Name: '),
                'Length': int(input('Book Length (Pages): ')),
                'Genre': input('Book Genre: ')}

    new_book['Author'] = generate_full_author(new_book['Author FN'],
                                              new_book['Author MN'],
                                              new_book['Author LN'])

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
                 6: 'Genre'}

    # Quickly generate the string
    prop_edit_prompt = ['[{}] {}'.format(key, value)
                        for key,value
                        in prop_dict.items()]
    prop_edit_prompt = '\n'.join(prop_edit_prompt)

    # Request Prompt
    prop_to_update = int(input(prop_edit_prompt + '\n'))
    prop_to_update = prop_dict[prop_to_update]

    # Get new value
    new_value = input('What is the new {} value: '.format(prop_to_update))

    # Change to integer if updating length
    new_value = int(new_value) if prop_to_update == 'Length' else new_value
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

            switch_mode = int(input('Would you like to [1] edit the existing '
                                    'entry or [2] overwrite the data: '))
            
            if switch_mode == 1:
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
                                    ignore_index = True)
    books_db.to_csv(db_path, index=False)

### Reading Database Updates

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
        return(finish - start).days

def add_reading_entry(reading_db, book_title):
    """ Adds a new reading entry for a book
    
    Inputs:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        book_title -- Title of book to use for the entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with new reading entry
    """

    print('Please enter the following optional information for a new entry:')

    # Get optional information
    start_date = pd.to_datetime(input('Start Date (Optional): ')).date()
    finish_date = pd.to_datetime(input('End Date (Optional): ')).date()

    # Create temporary entry object
    new_entry_dict = {'Title': book_title,
                    'Start': start_date,
                    'Finish': finish_date,
                    'Reading Time': update_reading_time(start_date,
                                                        finish_date)
                    }

    return(reading_db.append(new_entry_dict, ignore_index = True))

def edit_reading_entry(reading_db, book_title):
    """ Edits properties of an existing reading entry
    
    Inputs:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        book_title -- Title of book to filter for the reading entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with updated entriy
    """

    print_filtered_db(reading_db, book_title)

    index_to_edit = int(input('Which entry (index) would you like to edit?: '))

    print('Which property would you like to edit?')

    # TODO: Enable editing of the title
    # TODO: Have a way to catch unacceptable inputs

    property_to_update = int(input('[1] Start | [2] Finish (Pass the number): '))
    property_to_update = 'Start' if (property_to_update == 1) else 'Finish'
    new_property_val = pd.to_datetime(input('What is the new date?: ')).date()
    reading_db.loc[index_to_edit, property_to_update] = new_property_val

    # Do autoupdate of reading time
    new_time = update_reading_time(reading_db.loc[index_to_edit, 'Start'],
                                   reading_db.loc[index_to_edit, 'Finish'])
    reading_db.loc[index_to_edit, 'Reading Time'] = new_time

    return(reading_db)

def remove_reading_entry(reading_db, book_title):
    """ Removes a reading entry
    
    Inputs:
        reading_db {DataFrame} -- Pandas DataFrame of the reading database
        book_title -- Title of book to filter for the reading entry

    Outputs:
        reading_db {DataFrame} -- DataFrame with removed entry
    """

    print_filtered_db(reading_db, book_title)
    index_to_remove = int(input('Which entry (index) would '
                                'you like to remove?: '))
    return(reading_db.drop(index_to_remove))


def update_reading_db(db_directory):
    """ Main function to update book database

    Inputs:
        db_directory {string} -- Path to the data directory

    Outputs:
        Saves an updated reading database as a csv to the disk
    """


    # Read in the datbase
    db_path = db_directory + '/' + 'reading.csv'
    reading_db = pd.read_csv(db_path)

    # Requires additional formatting for dates
    reading_db['Start'] = pd.to_datetime(reading_db['Start']).dt.date
    reading_db['Finish'] = pd.to_datetime(reading_db['Finish']).dt.date

    # Print full database for ease of viewing
    print_db(db_path)

    update_mode = int(input('Do you want to [1] add a new entry, [2] edit a'
                            'current entry, or [3] remove an entry?: '))

    book_title = prompt_for_title(reading_db, update_mode)

    if update_mode == 1:
        if book_title in reading_db['Title'].values:
            print('An entry for {} already exists.'.format(book_title))
            switch_to_edit = input('Would you like to edit an entry instead '
                                   '[Y/N]?: ')
            if switch_to_edit in ['Y', 'y']:
                reading_rb = edit_reading_entry(reading_db, book_title)
            else:
                reading_db = add_reading_entry(reading_db, book_title)
        else:
            reading_db = add_reading_entry(reading_db, book_title)

    elif update_mode == 2:
        reading_db = edit_reading_entry(reading_db, book_title)
    else:
        reading_db = remove_reading_entry(reading_db, book_title)

    reading_db.sort_values(['Finish', 'Start'], na_position='last',
                           inplace=True)
    reading_db.to_csv(db_path, index=False)