-- table structures for tuttibot
GRANT USAGE ON SCHEMA cron TO postgres;


create schema roast_my_code;


create table roast_my_code.roast (
	id serial,
    github_user text,
    create_ts timestamp default CURRENT_TIMESTAMP
);
