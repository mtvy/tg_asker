-- create database asker;
-- use asker;

-- create table chat_tb (
--     id serial primary key,
--     tid numeric(20, 0) unique,
--     chat varchar(128), 
--     add_date timestamp not null default now()
-- );

create table ask_tb (
    id serial primary key,
    head text, 
    sub varchar(64)[], 
    cid integer[],
    res jsonb,
    stat boolean,
    is_pub boolean,
    add_date timestamp not null default now()
);

-- create table active_tb (
--     id serial primary key,
--     cid integer REFERENCES chat_tb(id) on delete cascade on update cascade,
--     aid integer REFERENCES ask_tb(id) on delete cascade on update cascade,
--     mid integer,
--     res jsonb,
--     stat boolean,
--     add_date timestamp not null default now()
-- );
