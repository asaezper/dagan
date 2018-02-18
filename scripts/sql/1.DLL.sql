-- DDL
CREATE TABLE restaurant (
    res_id integer,
    name text not null,
    phone integer,
    web text,
    latitude REAL,
    longitude REAL,
    PRIMARY KEY(res_id)
);

CREATE TABLE menu (
    res_id integer REFERENCES restaurant(res_id),
    menu_id integer,
    name text not null,
    PRIMARY KEY(res_id, menu_id)
);

CREATE TABLE chat (
    chat_id integer,
    mute integer not null default 0,  -- 0/False, 1/True
    start_hour real not null default 12.25,
    end_hour real not null default 15,
    days text not null default '[0, 1, 2, 3]',
    PRIMARY KEY(chat_id)
);

CREATE TABLE subscription (
    chat_id integer not null,
    res_id integer REFERENCES restaurant(res_id),
    menu_id integer REFERENCES menu(menu_id),
    PRIMARY KEY(chat_id, res_id, menu_id)
);

CREATE TABLE menu_report (
    chat_id integer not null,
    res_id integer REFERENCES restaurant(res_id),
    menu_id integer REFERENCES menu(menu_id),
    report_date datetime not null default (DATETIME('now')),
    mode integer not null default 0, -- 0: Manual / 1: Automatico
    PRIMARY KEY(chat_id, res_id, menu_id, report_date)
);

CREATE TABLE scheduled_search (
    chat_id integer REFERENCES chat(chat_id),
    text_to_search text,
    PRIMARY KEY(chat_id, text_to_search)
);

CREATE TABLE search_report (
    chat_id integer not null REFERENCES chat(chat_id),
    text_to_search text,
    results integer not null,
    search_date datetime not null default (DATETIME('now')),
    mode integer not null default 0, -- 0: Manual / 1: Automatico
    PRIMARY KEY(chat_id, text_to_search, search_date)
);

