DROP TABLE IF EXISTS USERS; 


CREATE TABLE USERS (
    id    SERIAL,
    f_name VARCHAR(30),
    l_name VARCHAR(30),
    u_name VARCHAR(15),
    password VARCHAR(255),
    profile_url VARCHAR(255),
    PRIMARY KEY(id) 
)