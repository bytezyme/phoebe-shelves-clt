"""Utility methods for parsing user inputs via input().

This module provides common utility functions for accepting and validating
user inputs via the input() method.
"""

import pandas as pd
import dateutil


def prompt_from_choices(choices, prompt=None, zero_indexed=False):
    """Prompt from a list of choices"""

    # Get list of all of the options
    if zero_indexed:
        choices_index = list(range(0, len(choices)))
    else:
        choices_index = list(range(1, len(choices) + 1))

    if prompt is None:
        prompt = ['[{}] {}'.format(index, value)
                  for index, value
                  in zip(choices_index, choices)]
        prompt = '\n'.join(prompt) + '\nSelection: '

    while True:
        try:
            selection = int(input(prompt))
            if selection not in choices_index:
                raise ValueError

            if zero_indexed:
                return(choices[selection])
            else:
                return(choices[selection - 1])

        except ValueError:
            print('Please enter one of the valid options.\n')


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


def confirm(prompt, sep=': '):
    """Prompts the user with a yes/no prompt

    Args:
        prompt {string} -- Prompt user sees on the command-line
        sep (opt) {string} -- Separator symbol between prompt and input

    Outputs:
        selection {bool} -- True if user indicates "yes"

    """

    final_prompt = prompt + ' [y/N]{}'.format(sep)
    selection = input(final_prompt).upper()

    while selection not in {'Y', 'N', 'YES', 'NO'}:
        selection = input('Please choose [y/N]{}'.format(sep)).upper()

    return(selection == 'Y' or selection == 'YES')
