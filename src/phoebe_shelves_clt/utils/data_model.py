""" Backend data models for the overall script

This module provides the classes and functions that encompass the backend
data. This is primarily used to provide a more concise way of interacting
with the CSV backend that can simulate similar programming patterns as
interacting with the SQL backend.
"""

from typing import Dict, List, Set

import pandas as pd
import numpy as np

# Type Aliases
DataFrame = pd.DataFrame
Series = pd.Series

class CSVDataModel:
    """ Backend data model during user interaction and processing

    Attributes:
        data_directory: Path to the data directory
        model_data (Dict[str: DataFrame]): Dictionary of table names to the
            respective DataFrame representation.
        csv_list (List[str]): List of the component CSV file names.
    """

    def __init__(self, data_directory: str):
        """ Initializes the CSVDataModel with the appropriate data

        Initializes a new CSVDataModel using data located in a specified
        data directory.

        Args:
            self: The current CSVDataModel instance.
            data_directory: Path to the data directory.
        """
        self.data_directory = data_directory
        self.model_data = self.load_model()

    def load_model(self) -> Dict[str, DataFrame]:
        """ Read in all component CSV tables

        Reads in all component CSV tables into a Pandas DataFrame for use in
        downstream processing and merging.

        Args:
            self: The current CSVDataModel instance.
        
        Returns:
            data_model (Dict[str: DataFrame]): Dictionary of table names to the
            respective DataFrame representation.
        """
        data_model = {}
        for name in self.csv_list:
            path = f"{self.data_directory}/backend/{name}.csv"
            data_model[name] = pd.read_csv(path)

            # Need to fill NA for string concatenation later on
            if name == "authors":
                data_model[name].fillna("", inplace=True)
        return(data_model)

    csv_list = ["authors", "books", "genres", "reading", "series",
                "books_authors", "books_genres", "books_series"]

    ### --------------------- Retrieve basic lists ------------------------ ###

    def get_authors_dict(self) -> Dict[str, int]:
        """ Retrieve dictionary of authors.

        Retrieves dictionary of all author names and their author ID's for use
        in later processing steps and prompting.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            Dictionary mapping from the formatted author names to their
            respective author IDs.
        """
        authors = self.create_authors_formatted()
        return(dict(zip(authors["Author"], authors["id"])))

    def get_books_dict(self) -> Dict[str, int]:
        """ Retrieve dictionary of book titles.

        Retrieves a dictionary of all of the books titles and their respective
        book ID's for use in later processing steps and prompting.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            Dictionary mapping from the book titles to their respective
            book IDs.
        """
        return(dict(zip(self.model_data["books"]["title"],
                        self.model_data["books"]["id"])))

    def get_genres_dict(self) -> Dict[str, int]:
        """ Retrieve dictionary of genres.

        Retrieves a dictionary of all of the genres and their respective genre
        ID's for use in later processing steps and prompting.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            Dictionary mapping from the genre names to their respective
            genre IDs.
        """
        return(dict(zip(self.model_data["genres"]["name"],
                        self.model_data["genres"]["id"])))

    ### --------------------- Main database views ------------------------- ###

    def generate_main_books(self, filter: str = None,
                            **kwargs) -> DataFrame:
        """ Generate the user-friendly books database/table

        Generate the user-friendly books database that is an aggregation of
        the individual backend tables within the CSV-based data model. This
        method also supports filtering the data during the merging process.

        Arguments:
            self: Current CSVDataModel instance.
            to_filter: Flag to indicate a filter should be applied.

        Keyword Arguments:
            column (str): Indicates which column to filter on.
            id_list (int): List of ID numbers (from different columns) to
                filter for.
            comp_type (int): Indicates which comparison type (for numeric
                or date) to utilize.
            thresholds (List[int]): List of threshold values to compare to.

        Returns:
            main_books: Fully-formatted and filtered books database.
        """
        # Generate component aggregates
        books_authors_merged = self.create_book_authors_merge()
        books_genres_merged = self.create_books_genres_merge()
        books_reading_agg = self.create_books_reading_agg()
        main_books = self.model_data["books"].copy()


        # Merge aggregates into the final
        main_books = pd.merge(self.model_data["books"],
                              books_authors_merged,
                              left_on="id", right_on="book_id"
                              ).drop(columns=["book_id"])
        main_books = pd.merge(main_books, books_genres_merged,
                              left_on="id", right_on="book_id",
                              ).drop(columns=["book_id"])
        main_books = pd.merge(main_books, books_reading_agg,
                              left_on="id", right_on="book_id")
        main_books["Rating"] = main_books.apply(lambda row: \
            self.merge_ratings(row), axis=1)
        main_books.rename(columns={"id": "ID", "title": "Title",
                                   "book_length": "Pages", "Genre": "Genres"},
                          inplace=True)  # type: ignore
        
        if filter is None:
            pass
        elif filter == "Author":
            data_filter = main_books["author_id"].apply(lambda authors: \
                self.check_all_in_set(kwargs["id_list"], authors))
            main_books = main_books[data_filter]

        elif filter == "Genre":
            data_filter = main_books["genre_id"].apply(lambda genres: \
                self.check_all_in_set(kwargs["id_list"], genres))
            main_books = main_books[data_filter]

        elif filter == "Title":
            #! This approach can be expanded to accept multiple titles
            data_filter = main_books["ID"].apply(lambda title: \
                title in kwargs["id_list"])
            main_books = main_books[data_filter]

        elif filter == "Rating":
            data_filter = self.numeric_filter(\
                main_books, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_books = main_books[data_filter]

        elif filter == "Pages":
            data_filter = self.numeric_filter(\
                main_books, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_books = main_books[data_filter]

        else:  # Times Read
            data_filter = self.numeric_filter(\
                main_books, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_books = main_books[data_filter]

        new_column_order = ["ID", "Title", "Author(s)", "Rating",
                            "Pages", "Times Read", "Genres"]
        main_books = main_books.reindex(columns=new_column_order)  # type: ignore
        main_books.set_index("ID", inplace=True)
        main_books.sort_values("Title")
        return(main_books)

    def generate_main_reading(self, filter: str = None,
                              **kwargs) -> DataFrame:
        """ Generate the user-friendly reading database/table

        Generate the user-friendly reading database that is an aggregation of
        the individual backend tables within the CSV-based data model. This
        method also supports filtering the data during the merging process.

        Arguments:
            self: Current CSVDataModel instance.
            to_filter: Flag to indicate a filter should be applied.

        Keyword Arguments:
            column (str): Indicates which column to filter on.
            id_list (int): List of ID numbers (from different columns) to
                filter for.
            comp_type (int): Indicates which comparison type (for numeric
                or date) to utilize.
            thresholds (List[int]): List of threshold values to compare to.

        Returns:
            main_books: Fully-formatted and filtered reading database.
        """
        books_authors_merge = self.create_book_authors_merge()
        main_reading = pd.merge(self.model_data["reading"], books_authors_merge,
                                on="book_id")
        main_reading = pd.merge(main_reading, self.model_data["books"][["id", "title"]],
                                left_on="book_id", right_on="id"
                                ).drop(columns=["id_y"])

        # Date-based columns require some type processing
        main_reading["start_date"] = pd.to_datetime(main_reading["start_date"]).dt.date
        main_reading["finish_date"] = pd.to_datetime(main_reading["finish_date"]).dt.date
        main_reading["read_time"] = (main_reading["finish_date"] - main_reading["start_date"]).dt.days
        main_reading.round({"read_time": 0})

        main_reading.rename(columns={"id_x": "ID", "start_date": "Start",
                                     "finish_date": "Finish",
                                     "rating": "Rating", "title": "Title",
                                     "read_time": "Read Time"},
                            inplace=True)

        if filter is None:
            pass
        elif filter == "Author":
            data_filter = main_reading["author_id"].apply(lambda authors: \
                self.check_all_in_set(kwargs["id_list"], authors))
            main_reading = main_reading[data_filter]

        elif filter == "Title":
            #! This approach can be expanded to accept multiple titles
            data_filter = main_reading["book_id"].apply(lambda title: \
                title in kwargs["id_list"])
            main_reading = main_reading[data_filter]

        elif filter == "Start":
            data_filter = self.date_filter(\
                main_reading, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_reading = main_reading[data_filter]

        elif filter == "Finish":
            data_filter = self.date_filter(\
                main_reading, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_reading = main_reading[data_filter]

        elif filter == "Read Time":
            data_filter = self.numeric_filter(\
                main_reading, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_reading = main_reading[data_filter]

        else:  # Rating
            data_filter = self.numeric_filter(\
                main_reading, filter, kwargs["comp_type"],
                kwargs["thresholds"])
            main_reading = main_reading[data_filter]
                
        new_col_order = ["ID", "Title", "Author(s)", "Start", "Finish", "Rating", "Read Time"]
        main_reading = main_reading.reindex(columns=new_col_order)  # type: ignore
        main_reading.set_index("ID", inplace=True)
        main_reading.sort_values("Finish", inplace=True)
        return(main_reading)


    ### ------------------ Table Merging and Formatting ------------------- ###

    def create_authors_formatted(self) -> DataFrame:
        """ Generate fully-formatted authors table

        Generates a fully-formatted authors table that combines the individual
        columns from the backend authors.csv into the standard name format.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            authors_formatted: DataFrame consisting of the author ID and the
                formatted name.
        """
        authors_formatted = self.model_data["authors"].copy()
        authors_formatted["Author"] = authors_formatted.apply(lambda row: self.merge_names(row), axis=1)
        authors_formatted.drop(columns=["first_name", "middle_name", "last_name", "suffix"], inplace=True)
        return(authors_formatted)


    def create_book_authors_merge(self) -> DataFrame:
        """ Merge formatted authors table into the books_authors mapping table

        Merge the formatted authors table into the books_authors mapping table
        to generate a final mapping table between a book ID, a comma-separated
        author string, and an associated set of author IDs. This will be merged
        into the books table for the final user-friendly representation.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            books_authors_merged: Merged table from the formatted authors
                temporary table and the books_authors mapping table.
        """
        authors_temp = self.create_authors_formatted()
        books_authors_temp = pd.merge(self.model_data["books_authors"],
                                      authors_temp, left_on="author_id",
                                      right_on="id").drop(columns=["id"])

        books_authors_grouped = books_authors_temp.groupby("book_id")
        agg_dict = {"Author": lambda name: ", ".join(name),
                    "author_id": lambda id: set(id)}
        books_authors_merged = books_authors_grouped.agg(agg_dict).reset_index()

        books_authors_merged.rename(columns={"Author": "Author(s)"}, inplace=True)
        return(books_authors_merged)


    def create_books_genres_merge(self) -> DataFrame:
        """ Merge the genres table into the books_genres mapping table

        Merge the genres table into the books_genres mapping table to generate
        a final mapping table between a book ID, a comma-separted genre string,
        and an associated set of genre IDs. This will be merged into the books
        table for the final user-friendly representation.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            books_authors_merged: Merged table from the genres table and the
                books_genres mapping table.
        """
        books_genres_temp = pd.merge(self.model_data["books_genres"],
                                     self.model_data["genres"],
                                     left_on="genre_id", right_on="id"
                                     ).drop(columns=["id"])

        books_genres_grouped = books_genres_temp.groupby("book_id")
        agg_dict = {"name": lambda name: ", ".join(name),
                    "genre_id": lambda id: set(id)}
        books_genres_merged = books_genres_grouped.agg(agg_dict).reset_index()

        books_genres_merged.rename(columns={"name": "Genre"}, inplace=True)
        return(books_genres_merged)


    def create_books_reading_agg(self):
        """ Create a grouped-and-aggregated reading table by book ID.

        Create an aggregated reading table that is grouped by the book ID. The
        aggregations include 1) the average of the ratings per book and 2) the
        time delta between the start and finish dates for each entry (row).
        This will be merged into the books table for the final user-friendly
        representation.

        Args:
            self: Current CSVDataModel instance.

        Returns:
            books_reading_agg: Group-and-aggregated reading table.
        """
        books_reading_agg = self.model_data["reading"].groupby("book_id").agg({"rating": "mean", "finish_date": "count"})
        books_reading_agg.rename(columns={"rating": "avg_rating", "finish_date": "Times Read"}, inplace=True)
        return(books_reading_agg)


    ### ------------------ Data Processing and Management ----------------- ###

    def merge_names(self, row: Series) -> str:
        """ Merge name components into a final formatted name.

        Merge the four basic components of an author's name into a final
        formatted name. This method supports omitting different components
        while maintaining proper formatting (no extra spaces or punctuation).

        Args:
            self: Current CSVDataModel instance.
            row: The author row containing the four name components.
        
        Returns:
            final_name: The full author name string.
        """
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

    def merge_ratings(self, row: Series) -> float:
        """ Merge the ratings from the reading and books backend table

        Merges the overall book rating from the books backend table and the
        average rating from the aggregated reading table. If there is a valid
        average rating from the reading table, it will be used. Otherwise, the
        overall book rating from the books backend table is used.

        Args:
            self: Current CSVDataModel instance.
            row: Current main books row entry.
        
        Returns:
            (float): The average rating (if available) or the overall rating.
        """
        if np.isnan(row.avg_rating):
            return(row.rating)
        else:
            return(row.avg_rating)

    def check_all_in_set(self, start_list: List, target_set: Set) -> bool:
        """ Checks if all elements of a list exists in another set

        Checks if all of the elements in a starting list exist in another set.
        If this is not the case, then the method returns false.

        Args:
            self: Current CSVDataModel instance.
            start_list: List of elements to check.
            target_set: Set of elements to check against.

        Returns:
            (bool): True if all elements in the start_list exist in the
                target_set.
        """
        is_in_set = False
        for element in start_list:
            if element in target_set:
                is_in_set = True
        return(is_in_set)


    def date_filter(self, data: DataFrame, column: str,
                    comp_type: int, thresholds: List) -> Series:
        """ Filter a date-based column from one of the databases

        Generates a boolean filter by comparing the values of a date-like
        column to given threshold values. This includes: 1) filtering for
        entries after a given date, 2) filtering for entries before a giving
        date, 3) filtering for entries between given dates, 4) filtering for
        from a sepecific year, and 5) filtering for entries with missing dates.

        Args:
            self: Current CSVDataModel instance.
            data: The initial DataFrame to filter.
            column: The column to filter on.
            comp_type: The comparison type to use.
            thresholds: Thresholds to compare values to.

        Returns:
            data_filter: A Series containing the Boolean filter for the
                comparison.
        """
        if comp_type == 1:
            data_filter = data[column] >= thresholds[0]
        elif comp_type == 2:
            data_filter = data[column] <= thresholds[0]
        elif comp_type == 3:
            lower_filter = data[column] >= thresholds[0]
            upper_filter = data[column] <= thresholds[1]
            data_filter = lower_filter & upper_filter
        elif comp_type == 4:
            data_filter = pd.to_datetime(data[column]).dt.year == \
                thresholds[0].year
        else:  # comp_type == 5
            data_filter = data[column].isnull()
        
        return(data_filter)

    def numeric_filter(self, data, column, comp_type, thresholds):
        """ Filter a numeric column from one of the databases

        Generates a boolean filter by comparing the values of a numeric
        column to given threshold values. This includes: 1) filtering for
        entries less than a certain value, 2) filtering entries greater than
        a certain value, 3) filtering entries in a range of values, and 4)
        filtering entries that are missing a value.

        Args:
            self: Current CSVDataModel instance.
            data: The initial DataFrame to filter.
            column: The column to filter on.
            comp_type: The comparison type to use.
            thresholds: Thresholds to compare values to.

        Returns:
            data_filter: A Series containing the Boolean filter for the
                comparison.
        """
        if comp_type == 1:
            data_filter = data[column] <= thresholds[0]
        elif comp_type == 2:
            data_filter = data[column] >= thresholds[0]
        elif comp_type == 3:
            lower_filter = data[column] >= thresholds[0]
            upper_filter = data[column] <= thresholds[1]
            data_filter = lower_filter & upper_filter
        else:  # comp_type == 4
            data_filter = data[column].isnull()
        return(data_filter)