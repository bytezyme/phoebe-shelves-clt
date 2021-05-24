import pandas as pd

from phoebe_shelves_clt.utils import data_processing

class CSVDataModel:
    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.model_data = self.load_model()

    def load_model(self):
        data_model = {}
        for name in self.csv_list:
            path = f"{self.data_directory}/backend/{name}.csv"
            data_model[name] = pd.read_csv(path)

            # Need to fill NA for string concatenation later on
            if name == "authors":
                data_model[name].fillna("", inplace=True)

        return(data_model)

    ### --------------------- Retrieve basic lists ------------------------ ###

    def get_authors_dict(self):
        authors = self.create_authors_formatted()
        return(dict(zip(authors["Author"], authors["id"])))

    def get_books_dict(self):
        return(dict(zip(self.model_data["books"]["title"],
                        self.model_data["books"]["id"])))

    def get_genres_dict(self):
        return(dict(zip(self.model_data["genres"]["name"],
                        self.model_data["genres"]["id"])))

    ### --------------------- Main database views ------------------------- ###




    def generate_main_books(self, to_filter: bool = False, **kwargs):
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
            data_processing.merge_ratings(row), axis=1)

        if to_filter:
            column = kwargs["column"]
            if column == "Author":
                author_filter = main_books["author_id"].apply(lambda row: \
                    data_processing.check_list_all_in_set(kwargs["id_list"], row))
                main_books = main_books[author_filter]
            elif column == "Genre":
                genre_filter = main_books["genre_id"].apply(lambda row: \
                    data_processing.check_list_all_in_set(kwargs["id_list"], row))
                main_books = main_books[genre_filter]
            elif column == "Title":
                title_filter = main_books["id"].apply(lambda row: \
                    data_processing.check_list_all_in_set(kwargs["id_list"], {row}))
                main_books = main_books[title_filter]
            elif column == "Rating":
                pass
            elif column == "Pages":
                pass
            else:
                pass

        main_books.rename(columns={"id": "ID", "title": "Title", "book_length": "Pages", "name": "Genres"}, inplace=True)  # type: ignore

        new_column_order = ["ID", "Title", "Author(s)", "Rating", "Pages", "Times Read", "Genre"]
        main_books = main_books.reindex(columns=new_column_order)  # type: ignore
        main_books.set_index("ID", inplace=True)
        return(main_books)

    def generate_main_reading(self):
        books_authors_merge = self.create_book_authors_merge()
        main_reading = pd.merge(self.model_data["reading"], books_authors_merge,
                                on="book_id")
        main_reading = pd.merge(main_reading, self.model_data["books"][["id", "title"]],
                                left_on="book_id", right_on="id"
                                ).drop(columns=["id_y", "book_id"])
        main_reading.rename(columns={"id_x": "ID", "start_date": "Start", "finish_date": "Finish",
                             "rating": "Rating", "title": "Title"}, inplace=True)
        new_col_order = ["ID", "Title", "Author(s)", "Start", "Finish", "Rating"]
        main_reading = main_reading.reindex(columns=new_col_order)  # type: ignore
        main_reading.set_index("ID", inplace=True)
        return(main_reading)

    def create_authors_formatted(self):
        authors_formatted = self.model_data["authors"].copy()
        authors_formatted["Author"] = authors_formatted.apply(lambda row: data_processing.merge_names(row), axis=1)
        authors_formatted.drop(columns=["first_name", "middle_name", "last_name", "suffix"], inplace=True)
        return(authors_formatted)

    def create_book_authors_merge(self):
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

    def create_books_genres_merge(self):
        books_genres_temp = pd.merge(self.model_data["books_genres"],
                                     self.model_data["genres"],
                                     left_on="genre_id", right_on="id"
                                     ).drop(columns=["id"])
        books_genres_grouped = books_genres_temp.groupby("book_id")
        agg_dict = {"name": lambda name: ", ".join(name),
                    "genre_id": lambda id: set(id)}
        books_genres_merged = books_genres_grouped.agg(agg_dict).reset_index()
        books_genres_merged.rename(columns={"name": "Genre"}, inplace=True) # TODO: Rename to genres
        return(books_genres_merged)

    def create_books_reading_agg(self):
        books_reading_agg = self.model_data["reading"].groupby("book_id").agg({"rating": "mean", "finish_date": "count"})
        books_reading_agg.rename(columns={"rating": "avg_rating", "finish_date": "Times Read"}, inplace=True)
        return(books_reading_agg)


    csv_list = ["authors", "books", "genres", "reading", "series",
                "books_authors", "books_genres", "books_series"]