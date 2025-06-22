-- table structures for roast_my_code
GRANT USAGE ON SCHEMA cron TO postgres;


create schema roast_my_code;


create table roast_my_code.roast_style (
    id serial primary key,
    name text,
    llm_description text,
    active boolean,
    create_ts timestamp default CURRENT_TIMESTAMP
);


create table roast_my_code.roast (
    id serial primary key,
    github_user text,
    roast_style integer not null,
    create_ts timestamp default CURRENT_TIMESTAMP,
    constraint fk_roast_style
        foreign key(roast_style)
        references roast_my_code.roast_style(id)
);


create table roast_my_code.clapback (
    id serial primary key,
    llm_response text not null,
    audio_url text,
    open_api_cost float,
    create_ts timestamp default CURRENT_TIMESTAMP
);


CREATE TABLE roast_my_code.payitforward_credits (
    id INT PRIMARY KEY,
    remaining BIGINT NOT NULL
);

INSERT INTO roast_my_code.payitforward_credits (id, remaining) VALUES (1, 0);
