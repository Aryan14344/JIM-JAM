// 1. Constraints & Indices
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE INDEX interaction_ts IF NOT EXISTS FOR ()-[r:REPLIED_TO]-() ON (r.timestamp);

// 2. Data Ingestion (Generic Template)
// LOAD CSV WITH HEADERS FROM 'file:///reddit_interactions.csv' AS row
// MERGE (u:User {username: row.source})
// MERGE (v:User {username: row.target})
// MERGE (u)-[r:REPLIED_TO {timestamp: toInteger(row.timestamp)}]->(v)
// ON CREATE SET r.weight = 1
// ON MATCH SET r.weight = r.weight + 1;

// 3. Quantile Pruning inside Neo4j (using GDS)
// Find the 75th percentile of weights across all relationships
MATCH ()-[r:REPLIED_TO]->()
WITH percentileCont(r.weight, 0.75) AS q3
MATCH ()-[r:REPLIED_TO]->()
WHERE r.weight < q3
DELETE r; // Prune 'slight' interactions directly in the DB

// 4. Identifying Structural Holes (Brokers) using Cypher/GDS
// A broker has a high degree but low clustering coefficient (their friends aren't friends)
CALL gds.localClusteringCoefficient.stream('myGraph')
YIELD nodeId, localClusteringCoefficient
WITH gds.util.asNode(nodeId) AS u, localClusteringCoefficient
MATCH (u)
WITH u, localClusteringCoefficient, count{(u)--()} AS degree
WHERE degree > 5
RETURN u.username, localClusteringCoefficient, degree
ORDER BY localClusteringCoefficient ASC, degree DESC
LIMIT 10;

// Explanation:
// - PercentileCont: Calculates the continuous percentile for the pruned threshold.
// - Local Clustering Coefficient: A standard proxy for Burt's Constraint. 
//   Low clustering = High structural hole brokerage potential.
