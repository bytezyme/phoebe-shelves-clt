from phoebe_shelves_clt.csv_backend import view_csv
from phoebe_shelves_clt.sql_backend import view_sql

def view_module(backend: str, db_select: str, mode, **kwargs):
    if backend == "csv":
        view_csv.main(db_select, mode, kwargs["data_directory"])
    else:
        view_sql.main(db_select, mode, kwargs["sql_configs"])