-- name: records_count
SELECT COUNT(*) AS total FROM medical_records WHERE user_id = %s;

-- name: medicines_count
SELECT COUNT(*) AS total FROM medicines
WHERE user_id = %s AND start_date <= CURDATE()
AND (end_date IS NULL OR end_date >= CURDATE());

-- name: appointments_count
SELECT COUNT(*) AS total FROM appointments
WHERE user_id = %s AND appointment_date >= NOW()
AND status = 'Scheduled';

-- name: metrics_count
SELECT COUNT(*) AS total FROM health_metrics WHERE user_id = %s;

-- name: upcoming_appointments
SELECT id, doctor_name, appointment_date, reason, status
FROM appointments
WHERE user_id = %s AND appointment_date >= NOW()
AND status = 'Scheduled'
ORDER BY appointment_date LIMIT 5;

-- name: recent_metrics
SELECT id, metric_type, value, unit, recorded_at
FROM health_metrics
WHERE user_id = %s
ORDER BY recorded_at DESC LIMIT 5;