DROP TABLE IF EXISTS results;

-- CREATE TABLE papers (
--      title text,
--      startDate int,
--      endDate int,
--      continuous bool,
--      code varChar(20),
--      PRIMARY KEY(code)
--     );
--
-- CREATE INDEX ON papers
--     (
--     code
--     );


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
    FOREIGN KEY(paperID) REFERENCES papers(code)
);

CREATE INDEX ON results (
    requestID, paperID
);