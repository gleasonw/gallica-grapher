CREATE TABLE papers (
    title text,
    lowYear int,
    highYear int,
    continuous bool,
    code text,
    primary key(code)
);

DROP TABLE IF EXISTS results;
CREATE TABLE results (
    id integer primary key generated always as identity,
    identifier text,
    year int,
    month int,
    day int,
    jstime int,
    searchTerm text,
    paperID text,
    requestIDForGettingProgress text,
    created timestamp,
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
    requestIDForGettingProgress text
);

CREATE INDEX ON holdingResults (
    requestIDForGettingProgress
);