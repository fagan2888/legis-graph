// Load historical bill sponsorships and co-sponsorships
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/sponsors-historical.csv'
AS line
MATCH (bill:Bill { billID: line.billID }),
      (legislator:Legislator { thomasID: line.thomasID })
MERGE (bill)-[r:SPONSORED_BY]->(legislator)
  ON CREATE SET r.cosponsor = CASE WHEN line.cosponsor = "1" THEN true ELSE false END;

// Load current bill sponsorships and co-sponsorships
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/sponsors-current.csv'
AS line
MATCH (bill:Bill { billID: line.billID }),
      (legislator:Legislator { bioguideID: line.bioguideID })
MERGE (bill)-[r:SPONSORED_BY]->(legislator)
    ON CREATE SET r.cosponsor = CASE WHEN line.cosponsor = "1" THEN true ELSE false END;
