-- name: find_user_by_email
SELECT id, name, email, password_hash
FROM users
WHERE email = %s;

-- name: register_user
INSERT INTO users (name, email, password_hash)
VALUES (%s, %s, %s);

-- name: get_user
SELECT id, name, email, phone, date_of_birth, created_at
FROM users
WHERE id = %s;

-- name: update_profile
UPDATE users
SET name = %s, phone = %s, date_of_birth = %s
WHERE id = %s;

-- name: delete_user
DELETE FROM users WHERE id = %s;