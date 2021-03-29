DROP TABLE papers;
CREATE TABLE papers (
     paperCode varChar(20),
     paperName text,
     startYear text,
     endYear text,
     url varChar(50),
     PRIMARY KEY(paperCode)
    );

COPY papers(paperName, startYear, endYear, url, paperCode)
FROM 'C:\Users\Public\paperDictionaryGoodDatesGoodNames.csv'
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