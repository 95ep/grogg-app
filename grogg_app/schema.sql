DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tastings;

CREATE TABLE users (
id SERIAL PRIMARY KEY,
username TEXT UNIQUE NOT NULL,
password TEXT NOT NULL,
activated BOOLEAN NOT NULL);

CREATE TABLE tastings (
id SERIAL PRIMARY KEY,
tasting_name TEXT NOT NULL,
created_by INTEGER NOT NULL,
creation_time TIMESTAMP NOT NULL,
join_code TEXT UNIQUE NOT NULL,
grogg_list TEXT[] NOT NULL,
current_grogg_idx INTEGER NOT NULL DEFAULT 0,
ratings INTEGER [][][] DEFAULT ARRAY[ARRAY[]::integer []],
rated_by TEXT[][] DEFAULT ARRAY[ARRAY[]::text[]]);