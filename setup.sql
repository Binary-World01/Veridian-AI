-- setup.sql

CREATE DATABASE IF NOT EXISTS veridian_db;
-- Change the password on this line
CREATE USER IF NOT EXISTS 'veridian_user'@'localhost' IDENTIFIED BY 'veridian123';
GRANT ALL PRIVILEGES ON veridian_db.* TO 'veridian_user'@'localhost';
FLUSH PRIVILEGES;