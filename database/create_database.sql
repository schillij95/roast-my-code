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


insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('TikTok Clapback', 'Gen-Z slang, use phrases like "No Cap" and "Straight Bussin"', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Gordon Ramsay', 'Harsh, culinary-themed insults, lots of swearing', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Corporate Speak', 'Buzzwords, jargon, and empty phrases', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Tech Bro', 'Silicon Valley lingo, startup culture references', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Movie Critic', 'Cinematic references, dramatic flair', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Old-Timey Radio Host', 'Vintage radio style, exaggerated politeness', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Corporate Buzzword Zombie', 'Overuse of buzzwords and jargon', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Edgy Teen from a 2000s CW Drama', 'Sarcastic, dramatic, and self-absorbed', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Clippy from MS Word', 'Annoying, overly helpful, with a sarcastic twist', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Disappointed Dad Energy', 'Stern, disappointed tone with dry humor', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Sarcastic Therapist', 'Psychological insights with a sarcastic edge', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Stack Overflow Commenter', 'Technical jargon with a condescending tone', true);
insert into roast_my_code.roast_style (name, llm_description, active) VALUES ('Reddit Moderator Power-Tripping', 'Overly authoritative and condescending', true);


create table roast_my_code.roast (
    id serial primary key,
    github_user text, -- either github user/repository or code, mutually exclusive
    github_repository text, -- either github user/repository or code, mutually exclusive
    code text, -- either github user/repository or code, mutually exclusive
    roast_style integer not null,
    create_ts timestamp default CURRENT_TIMESTAMP,
    constraint fk_roast_style
        foreign key(roast_style)
        references roast_my_code.roast_style(id)
);


create table roast_my_code.clapback (
    id serial primary key,
    roast_id integer,
    llm_response text not null,
    audio_url text,
    open_api_cost float,
    create_ts timestamp default CURRENT_TIMESTAMP,
    CONSTRAINT fk_roast 
        FOREIGN KEY(roast_id) 
        REFERENCES roast_my_code.roast(id)
);


CREATE TABLE roast_my_code.payitforward_credits (
    id INT PRIMARY KEY,
    remaining BIGINT NOT NULL
);

-- INSERT INTO roast_my_code.payitforward_credits (id, remaining) VALUES (1, 0);
INSERT INTO roast_my_code.payitforward_credits (id, remaining) VALUES (1, 100); -- debug value
