CREATE TEMP TABLE books_friendly AS (
    WITH 
        reading_agg (book_id, times_read, avg_rating) AS (
        SELECT
            book_id,
            COUNT(id) "times_read",
            AVG(rating)::NUMERIC(10,1) "avg_rating"
        FROM reading
        GROUP BY book_id
        ),

        books_authors_agg (book_id, authors) AS (
        SELECT
            ba.book_id,
            string_agg(COALESCE(a.first_name || ' ', '') || COALESCE(a.middle_name || ' ', '') || COALESCE(a.last_name, '') || COALESCE(', ' || a.suffix, ''), ', ')
        FROM books_authors ba
        INNER JOIN authors a
            ON ba.author_id = a.id {}
        GROUP BY
            ba.book_id
        ),

        books_genres_agg (book_id, genres) AS (
        SELECT
            bg.book_id,
            string_agg(g.name, ', ')
        FROM books_genres bg
        INNER JOIN genres g
            on bg.genre_id = g.id
        GROUP BY
            bg.book_id
        )

    SELECT
        b.title "Title",
        ba.authors "Author(s)",
        b.book_length "Pages",
        COALESCE(r.times_read, 0) "Times Read",
        COALESCE(r.avg_rating, b.rating::Numeric(10,1)) "Rating",
        bg.genres "Genre"
    FROM books b
    INNER JOIN books_authors_agg ba
        on b.id = ba.book_id
    LEFT JOIN reading_agg r
        on b.id = r.book_id
    LEFT JOIN books_genres_agg bg
        on b.id = bg.book_id
    {}
);
select * from books_friendly;