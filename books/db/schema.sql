DROP TABLE IF EXISTS USERS; 
DROP TABLE IF EXISTS BOOKS; 
DROP TABLE IF EXISTS REVIEWS; 


CREATE TABLE USERS (
    f_name VARCHAR(30),
    l_name VARCHAR(30),
    u_name VARCHAR(15),
    password VARCHAR(255),
    profile_url VARCHAR(255),
    PRIMARY KEY(u_name) 
);

CREATE TABLE BOOKS (
    ISBN VARCHAR(17),
    TITLE VARCHAR(250),
    author VARCHAR(250),
    year smallint,
    PRIMARY KEY(ISBN) 
);


CREATE TABLE REVIEWS(
    rating_id SERIAL,
    book_id VARCHAR(27) ,
    usr_id  VARCHAR(30) ,
    rate_count BIGINT ,
    rate_desc VARCHAR(255),
    FOREIGN KEY(book_id) REFERENCES BOOKS(ISBN),
    FOREIGN KEY(usr_id) REFERENCES USERS(u_name)
);