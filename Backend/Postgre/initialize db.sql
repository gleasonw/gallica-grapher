DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS papers;

CREATE TABLE papers (
     paperName text,
     startYear text,
     endYear text,
     paperCode varChar(20),
     PRIMARY KEY(paperCode)
    );

COPY papers(paperName, startYear, endYear, paperCode)
FROM '/mnt/c/Users/wglea/pycharmprojects/Gallica-Grapher/Backend/CSVdata/papersNoDuplicatesGoodDatesGoodNames.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE papers
    ALTER COLUMN startYear TYPE DATE using to_date(startYear, 'YYYY'),
    ALTER COLUMN endYear TYPE DATE using to_date(endYear, 'YYYY');

CREATE INDEX ON papers
    (
    paperCode,
    startYear,
    endYear
    );


CREATE TABLE results (
    identifier text,
    day integer,
    month integer,
    year integer,
    searchTerm text,
    paperID text,
    requestID text,
    PRIMARY KEY(identifier, requestID),
    FOREIGN KEY(paperID) REFERENCES papers(paperCode)
);




-- DROP TABLE papers CASCADE;
-- CREATE TABLE papers (
--      paperCode varChar(20),
--      paperName text,
--      startYear text,
--      endYear text,
--      url varChar(50),
--      PRIMARY KEY(paperCode)
--     );
--
-- COPY papers(paperName, startYear, endYear, url, paperCode)
-- FROM '/mnt/c/Users/Public/paperDictionaryGoodDatesGoodNames.csv'
-- DELIMITER ','
-- CSV HEADER;
--
-- ALTER TABLE papers
--     ALTER COLUMN startYear TYPE DATE using to_date(startYear, 'YYYY'),
--     ALTER COLUMN endYear TYPE DATE using to_date(endYear, 'YYYY');
--
-- CREATE INDEX ON papers
--     (
--     paperCode,
--     startYear,
--     endYear
--     );