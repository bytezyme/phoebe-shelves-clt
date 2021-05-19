"""Utility functions for updating database entries"""

from phoebe_shelves_clt.csv_backend import manage_csv
from phoebe_shelves_clt.sql_backend import manage_sql


def manage_module(backend: str, db_select: str, mode: str, **kwargs):
    if backend == "csv":
        manage_csv.main(db_select, mode, kwargs["data_directory"])
    else:
        manage_sql.main(db_select, mode, kwargs["sql_configs"])
    pass