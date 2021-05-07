"""Utility methods for parsing user inputs via input().

This module provides common utility functions for accepting and validating
user inputs via the input() method.
"""

import pandas as pd
import dateutil


def prompt_from_enum_options(prompt, options):
    """Prompt user to pass an integer associated with a set of options

    Args:
        prompt {string} -- Prompt that user sees on the command line
        options {set/list} -- Set/list of acceptable integer inputs

    Outputs:
        selection {int} -- Int representing the option selection
    """

    while True:
        try:
            selection = int(input(prompt))
            if selection not in options:
                raise ValueError
            return(selection)
        except ValueError:
            print('Please enter one of the valid options.\n')


def prompt_from_enum_dict(enum_dict):
    """Prompt user selection from dictionary with integer keys

    Args:
        enum_dict {dict} -- Dict mapping integer keys to options

    Outputs:
        {string} -- Dictionary value associated with
            the int selection
    """

    prompt = ['[{}] {}'.format(key, value)
              for key, value
              in enum_dict.items()]
    prompt = '\n'.join(prompt) + '\nSelection: '
    selection = prompt_from_enum_options(prompt, enum_dict.keys())
    return(enum_dict[selection])


def gen_enum_dict_from_list(values_list, zero_indexed=True):
    """Generates a dictionary with integer keys from a list

    Args:
        values_list {list} -- List of elements to use as dictionary values
        zero_indexed {bool} -- Indicates if keys should be zero- or one-indexed

    Outputs:
        {dict} -- Dictionary mapping integer keys to the input values list
    """

    if zero_indexed:
        keys = list(range(len(values_list)))
    else:
        keys = list(range(1, len(values_list) + 1))
    return(dict(zip(keys, values_list)))


def prompt_for_int(prompt):
    """Prompt user to input an integer

    This method requires the user to enter a valid integer. The user is
    prompted until a valid integer is passed.

    Args:
        prompt {string} -- Prompt user sees on the command line

    Outputs:
        {int} -- Validated integer from user input
    """

    while True:
        try:
            return(int(input(prompt)))
        except ValueError:
            print('Please enter a valid integer.\n')


def prompt_for_pos_int(prompt):
    """Prompt user to input a positive integer

    This method requires the user to enter a valid positive integer. The user
    is prompted until a valid positive integer is passed.

    Args:
        prompt {string} -- Prompt user sees on the command line

    Outputs:
        selection {int} -- Validated positive integer from user input
    """
    while True:
        try:
            selection = int(input(prompt))
            if selection < 0:
                raise ValueError
            return(selection)
        except ValueError:
            print('Please enter a positive integer.\n')


def prompt_for_date(prompt):
    """Prompt user to input a date

    This method requires a user to enter a string that can be correctly
    parsed as a dateutil.date object. The user is prompted until a properly
    formatted string is passed.

    Args:
        prompt {string} -- Prompt user sees on the command line

    Outputs:
        {datetime.date} -- Validated date from user input
    """

    while True:
        try:
            return(pd.to_datetime(input(prompt)).date())
        except(dateutil.parser._parser.ParserError, ValueError, OverflowError):
            print('Cannot parse the input as a date. Please try again.')


def prompt_for_yes(prompt):
    """Prompts user with a yes/no prompt

    Args:
        prompt {string} -- Prompt user sees on the command line

    Outputs:
        selection {bool} -- True if user passes 'Y' (yes)
    """
    selection = input(prompt).upper()

    while selection not in {'Y', 'N'}:
        selection = input('Please choose [Y/N]')
    return(selection == 'Y')


def confirm(prompt, sep=':'):
    """Prompts the user with a yes/no prompt

    Args:
        prompt {string} -- Prompt user sees on the command-line
        sep (opt) {string} -- Separator symbol between prompt and input

    Outputs:
        selection {bool} -- True if user indicates "yes"

    """

    final_prompt = prompt + ' [y/N]{} '.format(sep)
    selection = input(final_prompt).upper()

    while selection not in {'Y', 'N', 'YES', 'NO'}:
        selection = input('Please choose [y/N]: ').upper()

    return(selection == 'Y' or selection == 'YES')


def select_database(args, dir_path):
    if args.booksdb:
        db_select = 'books'
    elif args.readingdb:
        db_select = 'reading'
    else:
        db_select_prompt = ('Would you like to view the [1] books database or '
                            '[2] reading database?: ')
        db_select_opts = {1, 2}
        db_select = prompt_from_enum_options(db_select_prompt, db_select_opts)
        db_select = 'books' if db_select == 1 else 'reading'

    print('Using the {} database...'.format(db_select))
    return(db_select)
