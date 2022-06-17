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
    requestID, paperID
);