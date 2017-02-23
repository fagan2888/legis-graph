// Load House votes
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/votes-house.csv'
AS line
MATCH (bill:Bill { billID: line.billID }),
      (legislator:Legislator { bioguideID: line.bioguideID })
MERGE (bill)<-[r:VOTED_ON]-(legislator)
    ON CREATE SET r.vote = line.vote;

// Load Senate votes
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/votes-senate.csv'
AS line
MATCH (bill:Bill { billID: line.billID }),
      (legislator:Legislator { lisID: line.lisID })
MERGE (bill)<-[r:VOTED_ON]-(legislator)
    ON CREATE SET r.vote = line.vote;
