GRANT ALL PRIVILEGES
ON DATABASE marketplace_db
TO marketplace_user;

GRANT ALL
ON SCHEMA public
TO marketplace_user;

ALTER SCHEMA public
OWNER TO marketplace_user;

GRANT ALL PRIVILEGES
ON ALL TABLES IN SCHEMA public
TO marketplace_user;

GRANT ALL PRIVILEGES
ON ALL SEQUENCES IN SCHEMA public
TO marketplace_user;