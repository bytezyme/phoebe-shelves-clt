SELECT temp.*
FROM (
    SELECT
        COALESCE(a.first_name || ' ', '') || COALESCE(a.middle_name || ' ', '') || COALESCE(a.last_name, '') || COALESCE(', ' || a.suffix, '') "Author",
        a.id "ID"
    FROM authors a
) as temp
WHERE "Author" ilike '%{}%';