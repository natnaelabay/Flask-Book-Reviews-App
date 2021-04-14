DROP TABLE IF EXISTS USERS; 
DROP TABLE IF EXISTS BOOKS; 


CREATE TABLE USERS (
    id    SERIAL,
    f_name VARCHAR(30),
    l_name VARCHAR(30),
    u_name VARCHAR(15),
    password VARCHAR(255),
    profile_url VARCHAR(255),
    PRIMARY KEY(id) 
);

CREATE TABLE BOOKS (
    id    SERIAL,
    ISBN VARCHAR(17),
    TITLE VARCHAR(250),
    author VARCHAR(250),
    year smallint,
    PRIMARY KEY(id) 
);