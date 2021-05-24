import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.core.frame import DataFrame

from phoebe_shelves_clt.utils import inputs
from phoebe_shelves_clt.utils.data_model import CSVDataModel

# def print_db(db, db_select):
#     """Print database as formatted markdown table

#     Args:
#         db {DataFrame} -- Database
#         db_select {string} -- Indicates what database 'db' is

#     Outputs:
#         Prints formatted version of Pandas database to the terminal
#     """

#     if (db_select == 'books'):
#         db = db.drop(['Author FN', 'Author MN', 'Author LN'], axis='columns')

#     print('\n' + db.to_markdown(tablefmt='grid', index=False) + '\n')


# def print_db_title(db, book_title):
#     """Prints a filtered database to only include entries for a certain book

#     Args:
#         db {DataFrame} -- Books or reading database as a pandas DataFrame
#         book_title {string} -- Title of book to filter on

#     Outputs:
#         Prints formatted list (with index) of entires containing the book title
#     """

#     filtered_db = db[db['Title'] == book_title]
#     print('\n' + filtered_db.to_markdown(tablefmt='grid') + '\n')


# def numerical_threshold_filter(db, col_select):
#     """Use numerical thresholds to filter the database

#     Args:
#         db {DataFrame} -- Books or reading database as a pandas DataFrame
#         col_select {string} -- Column to filter on

#     Outputs:
#         db {DataFrame} -- Database filtered based on user-given thresholds
#     """

#     threshold_prompt = ('Would you like to filter based on [1] ≥ threshold'
#                         ', [2] ≤ threshold, or a [3] range?: ')
#     threshold_choices = [1, 2, 3]
#     threshold_mode = inputs.prompt_from_choices(threshold_choices,
#                                                 threshold_prompt)

#     lower_thresh_prompt = 'What\'s the smallest value (inclusive)?: '
#     upper_thresh_prompt = 'What\'s the largest value (inclusive)?: '

#     is_date = col_select in {'Start', 'Finish'}

#     if is_date:
#         prompt_function = inputs.prompt_for_date
#     else:
#         prompt_function = inputs.prompt_for_pos_int

#     if threshold_mode == 1:
#         lower_thresh = prompt_function(lower_thresh_prompt)
#         db = db[db[col_select] >= lower_thresh]
#     elif threshold_mode == 2:
#         upper_thresh = prompt_function(upper_thresh_prompt)
#         db = db[db[col_select] <= upper_thresh]
#     else:
#         lower_thresh = prompt_function(lower_thresh_prompt)
#         upper_thresh = prompt_function(upper_thresh_prompt)
#         upper_filter = db[col_select] <= upper_thresh
#         lower_filter = db[col_select] >= lower_thresh
#         db = db[upper_filter & lower_filter]

#     return(db)


# def date_filter(db, col_select):
#     """Use date thresholds to filter the database

#     Args:
#         db {DataFrame} -- Books or reading database as a pandas DataFrame
#         col_select {string} -- Column to filter on

#     Outputs:
#         db {DataFrame} -- Database filtered based on user-given thresholds
#     """

#     mode_prompt = ('Would you like to filter based on [1] an earliest date, '
#                    '[2] a latest date, [3] a range of dates, or [4] a '
#                    'specific year?: ')
#     mode_choices = [1, 2, 3, 4]
#     mode = inputs.prompt_from_choices(mode_choices, mode_prompt)

#     earliest_prompt = 'What\'s the earliest date you want to see?: '
#     latest_prompt = 'What\'s the latest date you want to see?: '
#     year_prompt = 'What year would you like to see?: '

#     if mode == 1:
#         threshold = inputs.prompt_for_date(earliest_prompt)
#         db = db[db[col_select] >= threshold]
#     elif mode == 2:
#         threshold = inputs.prompt_for_date(latest_prompt)
#         db = db[db[col_select] >= threshold]
#     elif mode == 3:
#         earliest_threshold = inputs.prompt_for_date(earliest_prompt)
#         latest_threshold = inputs.prompt_for_date(latest_prompt)
#         earliest_filter = db[col_select] >= earliest_threshold
#         latest_filter = db[col_select] <= latest_threshold
#         db = db[earliest_filter & latest_filter]
#     else:
#         year_threshold = inputs.prompt_for_date(year_prompt)
#         upper_threshold = year_threshold + pd.DateOffset(years=1)  # type: ignore
#         earliest_filter = db[col_select] >= year_threshold
#         latest_filter = db[col_select] <= upper_threshold
#         db = db[earliest_filter & latest_filter]

#     return(db)


# def books_filter(db):
#     """Filter books database based on user input

#     Args:
#         db {DataFrame} -- Books database as a pandas DataFrame

#     Outputs:
#         db {DataFrame} -- Database filtered based on user-given thresholds
#     """

#     cols = db.columns.drop(['Author FN', 'Author MN', 'Author LN'])
#     col_select = inputs.prompt_from_choices(cols)

#     numeric_cols = {'Length', 'Times Read', 'Rating'}

#     # Categorical, so get unique values and select from them
#     if col_select not in numeric_cols:
#         print('Choose the option from the list below: \n')

#         # Special Sort for Authors (present full author sort by last name)
#         if col_select == 'Author':
#             temp_df = db[['Author', 'Author LN']].sort_values(by=['Author LN'])
#             values = temp_df['Author'].unique()
#         else:
#             values = db[col_select].sort_values().unique()

#         values_select = inputs.prompt_from_choices(values)

#         if pd.isna(values_select):
#             db = db[pd.isna(db[col_select])]
#         else:
#             db = db[db[col_select] == values_select]
#     else:  # Numerical category, so use threshold filter
#         db = numerical_threshold_filter(db, col_select)
#     return(db)


# def reading_filter(db):
#     """Filter readingdatabase based on user input

#     Args:
#         db {DataFrame} -- Reading database as a pandas DataFrame

#     Outputs:
#         db {DataFrame} -- Database filtered based on user-given thresholds
#     """

#     col_select = inputs.prompt_from_choices(db.columns)

#     # Categorical, so get unique values and select from them
#     if col_select == 'Title':
#         print('Choose the option from the list below: \n')
#         titles = db[col_select].sort_values().unique()
#         title_select = inputs.prompt_from_choices(titles)
#         db = db[db[col_select] == title_select]
#     elif col_select in {'Start', 'Finish'}:
#         db = date_filter(db, col_select)
#     else:
#         db = numerical_threshold_filter(db, col_select)
#     return(db)


# def graphing_module(db, db_select, data_directory):
#     """ Graphing module for data

#     # TODO: Figure out best way to implement proper visualization
#     """

#     if db_select == "books":
#         pass
#     else:
#         # Fix date formats from datetime to date for groupby
#         db['Finish'] = pd.to_datetime(db['Finish'])
#         db['Start'] = pd.to_datetime(db["Start"])

#         db_finish = db.groupby(pd.Grouper(key='Finish', freq='MS'))["Title"].count()
#         db_finish = pd.DataFrame({'Monthly': db_finish.values, 'CSum': db_finish.cumsum()})
#         db_finish.index = db_finish.index.date  # type: ignore
#         _, ax = plt.subplots()
#         ax.bar(db_finish.index, db_finish["Monthly"], align='center')
#         ax2 = ax.twinx()
#         ax2.plot(db_finish.index, db_finish['CSum'])
#         ax.xaxis.set_major_locator(mdates.MonthLocator())
#         ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
#         plt.savefig(data_directory + '/test.png')


# def aggregation_module(db, db_select, data_directory):
#     """
#     TODO: Finish cleaning up reading db data aggregation
#     """

#     if db_select == "books":
#         """ Different Reports:
#             - Author: [Number of Books, Total Read Count, Average Read Count, Average Rating]
#             - Genre: [Number of Books, Total Read Count, Average Read Count, Average Rating]
#             - Rating: [Number of Books]
#             - Book: [Times Read, Average Reading Time]
#         """
#         print('WIP')
#     else:
#         """ Different Reports:
#             - Finish Month: [Books Read, Pages Read]
#         """

#         # Need books to merge book length

#         drop_list = ['Rating_x', 'Rating_y', 'Start', 'Reading Time',
#                      'Author', 'Author FN', 'Author MN', 'Author LN',
#                      'Times Read', 'Genre']
#         books_db = pd.read_csv(data_directory + '/books.csv')
#         merged_db = db.merge(books_db, on='Title').drop(columns=drop_list)

#         merged_db['Finish'] = pd.to_datetime(merged_db['Finish'])
#         merged_db = merged_db.groupby(pd.Grouper(key='Finish', freq='MS')).agg({'Title': 'count', 'Length': 'sum'})
#         merged_db.reset_index(inplace=True)
#         merged_db.columns = ['Month', 'Books Read', 'Pages Read']
#         merged_db['Month'] = merged_db['Month'].dt.date
#         print('\n' + merged_db.to_markdown(tablefmt='grid', index=False) + '\n')


# def main(db_select, mode, data_directory):
#     """Top-level flow to view databases

#     Args:
#         db_select {string} -- Indicates which database to work with
#         mode {string} -- Indicates which view mode to use
#         data_directory {string} -- Path to data directory

#     Outputs:
#         1. Prints a database as a table view to the command line
#         2. Prints database aggregate data to the command line
#     """

#     # Read in selected database
#     db_path = f'{data_directory}/{db_select}.csv'
#     db = pd.read_csv(db_path)

#     # Update column types if needed
#     if db_select == 'reading':
#         db['Start'] = pd.to_datetime(db['Start']).dt.date
#         db['Finish'] = pd.to_datetime(db['Finish']).dt.date

#     # Filter data if requested
#     to_filter_prompt = 'Would you like to search/filter the data first?'

#     if inputs.confirm(to_filter_prompt):
#         db = books_filter(db) if db_select == 'books' else reading_filter(db)

#     # Prepare data based on selected mode
#     if mode == 'table':
#         print_db(db, db_select)
#     elif mode == 'chart':
#         graphing_module(db, db_select, data_directory)
#     else:
#         aggregation_module(db, db_select, data_directory)



###############################################################################
###   NEW CODE                                                              ###
###############################################################################

def opt_filter(model: CSVDataModel, table: str, column: str):

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
        return(model.generate_main_books(to_filter=True, column=column, id_list=id_list))


def numeric_filter():
    pass

def date_filter():
    pass



def reading_filter(model):
    pass

def books_filter(model):
    opts = ["Title", "Author", "Times Read", "Rating", "Genre"]
    selection = inputs.prompt_from_choices(opts)

    if selection in {"Title", "Author", "Genre"}:
        return(opt_filter(model, "books", selection))

def print_table(db: DataFrame, show_index: bool = False):
    
    print("\n" + db.to_markdown(tablefmt='grid', index=show_index) + "\n")

def main(db_select, mode, model: CSVDataModel):
    # print(model.get_books_dict())

    to_filter_prompt = "Would you like to filter/search the data first?"
    to_filter = inputs.confirm(to_filter_prompt)

    if db_select == "reading" and to_filter:
        pass
    elif db_select == "reading" and not to_filter:
        db = model.generate_main_reading()
    elif db_select == "books" and to_filter:
        db = books_filter(model)
    else:
        db = model.generate_main_books()
    
    if mode == "table":
        print_table(db.fillna(""))