from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
# 加載 .env 配置
load_dotenv()

# Neo4j 配置
uri = os.getenv("NEO4J_URI_3068")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD_3068")
driver = GraphDatabase.driver(uri, auth=(username, password))

def find_statute_by_case_id(tx, case_id):
    query = (
        "MATCH (s:法條 {case_id: $case_id})"
        "RETURN s.text AS statute"
    )
    result = tx.run(query, case_id=case_id)
    record = result.single()
    if record:
        return record["statute"]
    else:
        return None


def get_statude_case(case_id):
    with driver.session() as session:
        statude = session.execute_read(find_statute_by_case_id, case_id)
        return statude
