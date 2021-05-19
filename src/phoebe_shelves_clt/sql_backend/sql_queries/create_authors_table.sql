CREATE TABLE authors (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    suffix TEXT,
    UNIQUE(first_name, middle_name, last_name, suffix)
);