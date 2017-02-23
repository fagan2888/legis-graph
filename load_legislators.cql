// Load 114th Congressional district geo data
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/114_districts_state.csv' AS line
MERGE (d:District {state: line.state, district: toInt(line.district)})
SET d.wkt = line.polygon;

// Load historical Legislators
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/legislators-historical.csv' AS line
MERGE (legislator:Legislator { bioguideID: line.bioguideID })
    ON CREATE SET legislator = line
    ON MATCH SET legislator = line
MERGE (s:State {code: line.state})
MERGE (legislator)-[:REPRESENTS]->(s)
FOREACH(party IN (CASE WHEN line.currentParty <> "" THEN [line.currentParty] ELSE [] END) |
    MERGE (p:Party {name: party})
    MERGE (legislator)-[:IS_MEMBER_OF]->(p)
)
MERGE (b:Body {type: line.type})
MERGE (legislator)-[:ELECTED_TO]->(b)
WITH line, legislator
MATCH (d:District) WHERE d.state=line.state AND d.district=toInt(line.district)
MERGE (legislator)-[:REPRESENTS]->(d);

// Load current Legislators
LOAD CSV WITH HEADERS
FROM 'http://localhost:8000/outputs/legislators-current.csv' AS line
MERGE (legislator:Legislator { bioguideID: line.bioguideID })
    ON CREATE SET legislator = line
    ON MATCH SET legislator = line
MERGE (s:State {code: line.state})
MERGE (legislator)-[:REPRESENTS]->(s)
MERGE (p:Party {name: line.currentParty})
MERGE (legislator)-[:IS_MEMBER_OF]->(p)
MERGE (b:Body {type: line.type})
MERGE (legislator)-[:ELECTED_TO]->(b)
WITH line, legislator
MATCH (d:District) WHERE d.state=line.state AND d.district=toInt(line.district)
MERGE (legislator)-[:REPRESENTS]->(d);

CREATE INDEX ON :Legislator(bioguideID);
CREATE INDEX ON :Legislator(thomasID);
CREATE INDEX ON :Legislator(lisID);
CREATE INDEX ON :Legislator(govtrackID);
CREATE INDEX ON :Legislator(opensecretsID);
CREATE INDEX ON :Legislator(votesmartID);
CREATE INDEX ON :Legislator(cspanID);
CREATE INDEX ON :Legislator(wikipediaID);
CREATE INDEX ON :Legislator(washpostID);
CREATE INDEX ON :Legislator(icpsrID);
