import numpy as np

def merge_names(row):
    final_name = ""

    if row.first_name != "":
        final_name += row.first_name + " "
    
    if row.middle_name != "":
        final_name += row.middle_name + " "
    
    if row.last_name != "":
        final_name += row.last_name

    if row.suffix != "":
        final_name += ", " + row.suffix
    
    return(final_name)

def merge_ratings(row):
    if row.avg_rating is not np.nan:
        return(row.avg_rating)
    else:
        return(row.rating)

def check_list_all_in_set(start_list, target_set):
    is_in_set = False
    for element in start_list:
        if element in target_set:
            is_in_set = True
    return(is_in_set)