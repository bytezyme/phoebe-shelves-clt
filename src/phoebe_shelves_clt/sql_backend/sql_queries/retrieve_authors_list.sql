select
    COALESCE(a.first_name || ' ', '') || COALESCE(a.middle_name || ' ', '') || COALESCE(a.last_name, '') || COALESCE(', ' || a.suffix, '') "Author",
    id "Author ID"
from authors a;