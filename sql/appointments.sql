-- name: list_appointments
SELECT id, doctor_name, appointment_date, reason, status
FROM appointments
WHERE user_id = %s
ORDER BY appointment_date DESC;

-- name: add_appointment
INSERT INTO appointments
(user_id, doctor_name, appointment_date, reason)
VALUES (%s, %s, %s, %s);

-- name: delete_appointment
DELETE FROM appointments WHERE id = %s AND user_id = %s;

-- name: complete_appointment
UPDATE appointments
SET status = 'Completed'
WHERE id = %s AND user_id = %s;