CREATE TABLE series (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    series_name TEXT,
    UNIQUE(series_name)
);