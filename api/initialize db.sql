DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS papers;

CREATE TABLE papers (
     title text,
     date text,
     code varChar(20),
     PRIMARY KEY(code)
    );

CREATE INDEX ON papers
    (
    code
    );


CREATE TABLE results (
    id integer primary key generated always as identity,
    identifier text,
    date text,
    searchTerm text,
    paperID text,
    requestID text,
    FOREIGN KEY(paperID) REFERENCES papers(code)
);