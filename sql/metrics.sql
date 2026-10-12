-- name: list_metrics
SELECT id, metric_type, value, unit, recorded_at, notes
FROM health_metrics
WHERE user_id = %s
ORDER BY recorded_at DESC;

-- name: add_metric
INSERT INTO health_metrics
(user_id, metric_type, value, unit, notes)
VALUES (%s, %s, %s, %s, %s);

-- name: chart_metrics
SELECT metric_type, value, unit, recorded_at
FROM health_metrics
WHERE user_id = %s
ORDER BY recorded_at ASC;