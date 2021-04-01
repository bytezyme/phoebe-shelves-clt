import dateutil
import pandas as pd

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

def prompt_for_column(col_dict):
    col_prompt = ['[{}] {}'.format(key, value)
                  for key, value
                  in col_dict.items()]
    col_prompt = '\n'.join(col_prompt) + '\nSelection: '
    col_selection = prompt_for_options(col_prompt, col_dict.keys())
    return(col_dict[col_selection])

# General Purpose Prompts

def prompt_for_pos_integer(input_prompt):

    while True:
        try:
            selection = int(input(input_prompt))
            if selection < 0:
                raise ValueError
            return(selection)
        except ValueError:
            print('Please enter a positive integer.\n')

def prompt_for_date(prompt):

    while True:
        try:
            return(pd.to_datetime(input(prompt)))
        except dateutil.parser._parser.ParserError:
            print('Cannot parse the input to a date. Please try again.')
