-- name: list_medicines
SELECT id, medicine_name, dosage, schedule_time,
       start_date, end_date, instructions
FROM medicines
WHERE user_id = %s
ORDER BY schedule_time;

-- name: add_medicine
INSERT INTO medicines
(user_id, medicine_name, dosage, schedule_time,
 start_date, end_date, instructions)
VALUES (%s, %s, %s, %s, %s, %s, %s);

-- name: delete_medicine
DELETE FROM medicines WHERE id = %s AND user_id = %s;

-- name: log_medicine
INSERT INTO medicine_logs (user_id, medicine_id, log_date, status)
SELECT %s, id, %s, %s
FROM medicines
WHERE id = %s AND user_id = %s
ON DUPLICATE KEY UPDATE status = VALUES(status);

-- name: medicine_logs_today
SELECT medicine_id, status
FROM medicine_logs
WHERE user_id = %s AND log_date = CURDATE();