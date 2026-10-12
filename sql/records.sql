-- name: list_records
SELECT id, title, record_type, record_date, notes
FROM medical_records
WHERE user_id = %s
ORDER BY record_date DESC;

-- name: add_record
INSERT INTO medical_records
(user_id, title, record_type, record_date, notes)
VALUES (%s, %s, %s, %s, %s);

-- name: delete_record
DELETE FROM medical_records WHERE id = %s AND user_id = %s;