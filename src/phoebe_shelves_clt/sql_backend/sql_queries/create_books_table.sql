CREATE TABLE books (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT,
    book_length INT,
    rating INT,
    UNIQUE(id, title)
);