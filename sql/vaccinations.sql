-- name: list_vaccinations
SELECT id, vaccine_name, dose_date, next_due_date, notes
FROM vaccinations
WHERE user_id = %s
ORDER BY next_due_date IS NULL, next_due_date;

-- name: add_vaccination
INSERT INTO vaccinations
(user_id, vaccine_name, dose_date, next_due_date, notes)
VALUES (%s, %s, %s, %s, %s);

-- name: delete_vaccination
DELETE FROM vaccinations WHERE id = %s AND user_id = %s;