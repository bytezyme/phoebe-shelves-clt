CREATE TABLE reading (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    book_id INT REFERENCES books(id) ON DELETE CASCADE,
    start_date DATE,
    finish_date DATE,
    rating INT,
    UNIQUE(id, book_id, start_date, finish_date)
);