create temp table reading_friendly AS (
    WITH 
        books_authors_agg (book_id, authors) AS (
        SELECT
            ba.book_id,
            string_agg(COALESCE(a.first_name || ' ', '') || COALESCE(a.middle_name || ' ', '') || COALESCE(a.last_name, '') || COALESCE(', ' || a.suffix, ''), ', ')
        FROM books_authors ba
        INNER JOIN authors a
            on ba.author_id = a.id {}
        GROUP BY
            ba.book_id
    )
    SELECT
        r.id "ID",
        b.title "Title",
        ba.authors "Author(s)",
        r.start_date "Start",
        r.finish_date "Finish",
        r.rating "Rating",
        r.finish_date - r.start_date + 1 "Read Time"
    FROM reading r
    INNER JOIN books b
        on r.book_id = b.id
    INNER JOIN books_authors_agg ba
        on b.id = ba.book_id
    {}
    ORDER BY
        r.finish_date ASC NUllS Last
);

SELECT * from reading_friendly;