CREATE TABLE books_authors (
    book_id INT REFERENCES books(id) ON DELETE CASCADE,
    author_id INT REFERENCES authors(id) ON DELETE CASCADE,
    PRIMARY KEY (author_id, book_id),
    UNIQUE(author_id, book_id)
);