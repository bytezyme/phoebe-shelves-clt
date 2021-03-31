import pandas as pd


def print_db(db_path):
    """ Print database as formatted markdown table

    Inputs:
        db_path {string} -- Path to data directory

    Outputs:
        Prints formatted version of Pandas database to the terminal
    """
    if (db_path.__contains__('books.csv')):
        db = pd.read_csv(db_path).drop(['Author FN', 'Author MN', 'Author LN'],
                                       axis='columns')
    else:
        db = pd.read_csv(db_path)

    print('\n' + db.to_markdown(tablefmt='grid', index=False) + '\n')


def print_filtered_db(db, book_title):
    """ Prints a filtered database to only include entries for a certain book

    Inputs:
        db {DataFrame} -- Books or reading database as a pandas DataFrame
        book_title -- Title of book to filter on

    outputs:
        Prints formatted list (with index) of entires containing the book title
    """
    filtered_db = db[db['Title'] == book_title]
    print('\n' + filtered_db.to_markdown(tablefmt='grid') + '\n')
