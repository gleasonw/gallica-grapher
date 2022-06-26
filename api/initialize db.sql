CREATE TABLE papers (
    title text,
    lowYear int,
    highYear int,
    continuous bool,
    code text,
    primary key(code)
);

CREATE TABLE results (
    id integer primary key generated always as identity,
    identifier text,
    year int,
    month int,
    day int,
    jstime int,
    searchTerm text,
    paperID text,
    requestID text,
    FOREIGN KEY (paperID) REFERENCES papers(code)
);

CREATE TABLE holdingResults (
    id integer primary key generated always as identity,
    identifier text,
    year int,
    month int,
    day int,
    jstime int,
    searchTerm text,
    paperID text,
    requestID text
);

CREATE INDEX ON holdingResults (
    requestID
);