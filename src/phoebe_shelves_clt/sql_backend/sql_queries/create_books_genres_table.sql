CREATE TABLE books_genres (
    book_id INT REFERENCES books(id) ON DELETE CASCADE,
    genre_id INT REFERENCES genres(id) ON DELETE CASCADE,
    UNIQUE(book_id, genre_id)
);