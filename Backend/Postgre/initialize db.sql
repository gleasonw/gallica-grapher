DROP TABLE papers;
CREATE TABLE papers (
     paperCode varChar(20),
     paperName text,
     startYear text,
     endYear text,
     digitalQuality FLOAT,
     url varChar(50),
     PRIMARY KEY(paperCode)
    );

COPY papers(paperName, startYear, endYear, digitalQuality, url, paperCode)
FROM '/Users/thefam/PycharmProjects/Gallica-Grapher/Backend/Postgre/Journals 1777-1950.csv'
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

