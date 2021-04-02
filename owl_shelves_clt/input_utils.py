""" Utility functions for parsing user inputs via input() method.

This function provides common utility functions for accepting and validating
user inputs via the input() method.
"""

import pandas as pd
import dateutil


def prompt_from_enum_options(prompt, options):
    """
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
    """ Prompt user selection from dictionary with integer keys

    """

    prompt = ['[{}] {}'.format(key, value)
              for key, value
              in enum_dict.items()]
    prompt = '\n'.join(prompt) + '\nSelection: '
    selection = prompt_from_enum_options(prompt, enum_dict.keys())
    return(enum_dict[selection])


def gen_enum_dict_from_list(values_list, zero_indexed=True):
    if zero_indexed:
        keys = list(range(len(values_list)))
    else:
        keys = list(range(1, len(values_list) + 1))
    return(dict(zip(keys, values_list)))


def prompt_for_int(prompt):
    while True:
        try:
            return(int(input(prompt)))
        except ValueError:
            print('Please enter a valid integer.\n')


def prompt_for_pos_int(prompt):
    while True:
        try:
            selection = int(input(prompt))
            if selection < 0:
                raise ValueError
            return(selection)
        except ValueError:
            print('Please enter a positive integer.\n')


def prompt_for_date(prompt):
    while True:
        try:
            return(pd.to_datetime(input(prompt)).date())
        except(dateutil.parser._parser.ParserError, ValueError, OverflowError):
            print('Cannot parse the input as a date. Please try again.')


def prompt_for_yes(prompt):
    selection = input(prompt).upper()

    while selection not in {'Y', 'N'}:
        selection = input('Please choose [Y/N]')
    return(selection == 'Y')
