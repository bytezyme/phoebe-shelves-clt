SELECT temp.*
FROM (
    SELECT
        a.first_name || a.middle_name || a.last_name "Author",
        a.id "ID"
    FROM authors a
) as temp
WHERE "Author" ilike '%{}%';