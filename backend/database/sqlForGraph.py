class SQLforGraph:

    def getSQLforSettings(self, timeBin, continuous):
        sqlSettings = {
            ("day", "false"): self.getDayGroupedSQL(),
            ("day", "true"): self.getDayGroupedExcludeIncompletePapersSQL(),
            ("month", "false"): self.getMonthGroupedSQL(),
            ("month", "true"): self.getMonthGroupedExcludeIncompletePapersSQL(),
            ("year", "false"): self.getYearGroupedSQL(),
            ("year", "true"): self.getYearGroupedExcludeIncompletePapersSQL(),
            ("gallicaYear", "false"): self.getGallicaGroupedYears(),
            ("gallicaMonth", "false"): self.getGallicaGroupedMonths()
        }
        return sqlSettings[(timeBin, continuous)]

    def getParamsForTicketWithSettings(self, ticketID, settings):
        if settings["continuous"] == 'true':
            return (
                settings["requestID"],
                ticketID,
                settings["startDate"],
                settings["endDate"],
                settings["averageWindow"]
            )
        elif settings["groupBy"] in ["gallicaYear", "gallicaMonth"]:
            return (
                settings["averageWindow"],
                settings["requestID"],
                ticketID
            )
        else:
            return (
                settings["requestID"],
                ticketID,
                settings["averageWindow"]
            )

    def getDayGroupedSQL(self):
        return """
        
        WITH binned_frequencies AS (
            SELECT year, month, day, count(*) AS mentions 
            FROM results 
            WHERE requestid = %s
            AND ticketid = %s 
            AND month IS NOT NULL
            AND day IS NOT NULL
            GROUP BY year, month, day 
            ORDER BY year, month, day),
            
            averaged_frequencies AS (
            SELECT year, month, day, AVG(mentions) 
            OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies)
            
        SELECT year, month, day, avgFrequency::float8
        FROM averaged_frequencies;
                
        """

    def getDayGroupedExcludeIncompletePapersSQL(self):
        return """
        
        WITH ticket_results AS 
            (SELECT year, month, day, papercode
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND month IS NOT NULL 
            AND day IS NOT NULL),
        
            binned_results_only_continuous AS 
            (SELECT year, month, day, count(*) AS mentions 
            FROM 
                ticket_results
                    
                JOIN papers 
                ON ticket_results.papercode = papers.code
                    AND papers.startdate <= %s
                    AND papers.enddate >= %s
                    AND continuous IS TRUE
                GROUP BY year, month, day 
                ORDER BY year, month, day),
                
            averaged_frequencies AS 
            (SELECT year, month, day, 
                AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_results_only_continuous)
        
        SELECT year, month, day, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def getMonthGroupedSQL(self):
        return """
        
        WITH binned_frequencies AS
            (SELECT year, month, count(*) AS mentions 
            FROM results continuous
            WHERE requestid = %s
            AND ticketid = %s 
            AND month IS NOT NULL
            GROUP BY year, month
            ORDER BY year,month),
        
            averaged_frequencies AS 
            (SELECT year, month, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies)
        
        SELECT year, month, avgFrequency::float8 
        FROM averaged_frequencies;
        """

    def getMonthGroupedExcludeIncompletePapersSQL(self):
        return """
        
        WITH ticket_results AS
            (SELECT year, month, papercode
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND month IS NOT NULL),
                
            binned_frequencies_only_continuous AS
                (SELECT year, month, count(*) AS mentions 
                FROM 
                    ticket_results

                    JOIN papers 
                    ON ticket_results.papercode = papers.code
                        AND papers.startdate <= %s
                        AND papers.enddate >= %s
                        AND continuous IS TRUE
                GROUP BY year, month
                ORDER BY year, month),
                
            averaged_frequencies AS
                (SELECT year, month, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
                FROM binned_frequencies_only_continuous)
                
        SELECT year, month, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def getYearGroupedSQL(self):
        return """
        
        WITH binned_frequencies AS
            (SELECT year, count(*) AS mentions 
            FROM results 
            WHERE requestid=%s
            AND ticketid = %s
            AND year IS NOT NULL
            GROUP BY year 
            ORDER BY year),
            
            averaged_frequencies AS
            (SELECT year, 
                    AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies)
            
        SELECT year, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def getYearGroupedExcludeIncompletePapersSQL(self):
        return """
        
        WITH ticket_results AS
            (SELECT year, papercode
            FROM results 
            WHERE requestid=%s
            AND ticketid=%s
            AND year IS NOT NULL),
            
            binned_frequencies_only_continuous AS
            (SELECT year, count(*) AS mentions 
            FROM 
                ticket_results

                JOIN papers 
                ON ticket_results.papercode = papers.code
                    AND papers.startdate <= %s
                    AND papers.enddate >= %s
                    AND continuous IS TRUE
                GROUP BY year
                ORDER BY year),
                
            averaged_frequencies AS
            (SELECT year,
                AVG(mentions) OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM binned_frequencies_only_continuous)
                
        SELECT year, avgFrequency::float8
        FROM averaged_frequencies;
        """

    def getGallicaGroupedYears(self):
        return """
        SELECT year, avgFrequency::float8 
        FROM (
            SELECT year, AVG(count) 
            OVER(ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (
                SELECT year, sum(count) as count
                FROM groupcounts
                WHERE requestid = %s
                AND ticketid = %s
                GROUP BY year
                ORDER BY year
            ) AS counts
        ) AS avgedCounts;
        """

    def getGallicaGroupedMonths(self):
        return """
        SELECT year, month, avgFrequency::float8
        FROM (
            SELECT year, month, AVG(count) 
            OVER (ROWS BETWEEN %s PRECEDING AND CURRENT ROW) AS avgFrequency
            FROM (
                SELECT year, month, sum(count) as count
                FROM groupcounts
                WHERE requestid = %s
                AND ticketid = %s
                GROUP BY year, month
                ORDER BY year, month
            ) AS counts
        ) AS avgedCounts;
        """
