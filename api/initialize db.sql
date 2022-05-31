DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS papers;

CREATE TABLE papers (
     paperName text,
     startYear date,
     endYear date,
     paperCode varChar(20),
     PRIMARY KEY(paperCode)
    );

CREATE INDEX ON papers
    (
    paperCode
    );


CREATE TABLE results (
    id integer primary key generated always as identity,
    identifier text,
    date date,
    searchTerm text,
    paperID text,
    requestID text,
    FOREIGN KEY(paperID) REFERENCES papers(paperCode)
);