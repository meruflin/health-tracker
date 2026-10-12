-- name: delete_user_reports
SELECT stored_filename FROM reports WHERE user_id = %s;

-- name: list_reports
SELECT id, title, original_filename, uploaded_at
FROM reports
WHERE user_id = %s
ORDER BY uploaded_at DESC;

-- name: add_report
INSERT INTO reports
(user_id, title, original_filename, stored_filename)
VALUES (%s, %s, %s, %s);

-- name: get_report
SELECT id, title, original_filename, stored_filename
FROM reports
WHERE id = %s AND user_id = %s;

-- name: delete_report
DELETE FROM reports WHERE id = %s AND user_id = %s;