"""Utility methods for parsing user inputs via input().

This module provides common utility functions for accepting and validating
user inputs via the input() method.
"""

from typing import Any, List

import pandas as pd
import dateutil


def prompt_from_choices(
        choices: List[Any],
        prompt: str = None,
        zero_indexed: bool = False,
        use_index: bool =True):
    """ Prompt from a list of choices
    
    Prompt the user from a list of potential choices. You can retrieve either
    the location of the choice in the initial choice list or use the
    automatically-generated selection index number. You can also indicate
    whether the choices should be presented starting at 0

    Args:
        choices: List of choices to present to the user
        prompt: Optional prompt to be used instead of generating a full list
        zero_indexed: Flag to indicate whether to use zero-indexing for options
        use_index: Flag to indicate whether to select on the index or actual value

    Returns:
        Any: The selected value
        Int: The location of the selected value in the provided list of choices
    """

    # Get list of all of the options
    if zero_indexed:
        choices_index = list(range(0, len(choices)))
    else:
        choices_index = list(range(1, len(choices) + 1))

    if prompt is None:
        prompt_list = [f'[{index}] {value}'
                       for index, value
                       in zip(choices_index, choices)]
        prompt = '\n'.join(prompt_list) + '\nSelection: '

    while True:
        try:
            selection = int(input(prompt))
            
            # Check for valid input
            if use_index:
                if selection not in choices_index:
                    raise ValueError
            else:
                if selection not in choices:
                    raise ValueError

        except ValueError:
            print('Please enter one of the valid options.\n')
        else:
            if use_index and zero_indexed:
                return(choices[selection])
            elif use_index and not zero_indexed:
                return(choices[selection - 1])
            elif not use_index and zero_indexed:
                return(choices[list(choices).index(selection)])
            else:
                return(choices[list(choices).index(selection) - 1])



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
            return(selection, selection)
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
            date_string = input(prompt)
            return(date_string, pd.to_datetime(date_string).date())
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

    final_prompt = f'{prompt} [y/N]{sep}'
    selection = input(final_prompt).upper()

    while selection not in {'Y', 'N', 'YES', 'NO'}:
        selection = input(f'Please choose [y/N]{sep}').upper()

    return(selection == 'Y' or selection == 'YES')
