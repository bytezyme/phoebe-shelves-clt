CREATE TABLE books_series (
    book_id INT REFERENCES books(id) ON DELETE CASCADE,
    series_id INT REFERENCES series(id) ON DELETE CASCADE,
    series_order INT,
    UNIQUE(book_id, series_id, series_order)
);