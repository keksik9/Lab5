from neo4j import GraphDatabase
from models import InsertRequest, Node

class Neo4jStorage:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def fetch_all_nodes(self):
        with self.driver.session() as session:
            query = "MATCH (n) RETURN n.id AS id, labels(n) AS labels"
            result = session.run(query)
            nodes = [{"id": record["id"], "label": record["labels"][0]} for record in result]
            return nodes

    def fetch_node_with_relationships(self, node_id):
        with self.driver.session() as session:
            query = """
                MATCH (n)-[r]->(m) WHERE n.id = $node_id
                RETURN n {.*} AS node_data, type(r) AS relationship_type, m.id AS end_node_id
            """
            result = session.run(query, node_id=node_id)
            node_info = None
            relationships = []
            for record in result:
                if not node_info:
                    node_info = {
                        "id": node_id,
                        "city": record["node_data"].get("home_town", ""),
                        "name": record["node_data"].get("name", ""),
                        "sex": record["node_data"].get("sex", 0),
                        "screen_name": record["node_data"].get("screen_name", "")
                    }
                relationships.append({
                    "relationship_type": record["relationship_type"],
                    "end_node_id": record["end_node_id"]
                })
            return {"node": node_info, "relationships": relationships}

    def create_node_and_relationships(self, data: InsertRequest):
        with self.driver.session() as session:
            query = """
                MERGE (n:User {id: $id})
                SET n.name = $name, n.screen_name = $screen_name, n.sex = $sex, n.home_town = $city
            """
            session.run(query, id=data.node.id, name=data.node.name,
                        screen_name=data.node.screen_name, sex=data.node.sex,
                        city=data.node.city)
            # Create relationships
            for rel in data.relationships:
                if rel.type.upper() not in ["FOLLOWS", "SUBSCRIBES"]:
                    continue
                end_node_label = self.get_node_label_by_id(rel.end_node_id)
                query = f"""
                    MATCH (n:User {{id: $id}})
                    MATCH (m:{end_node_label} {{id: $end_node_id}})
                    MERGE (n)-[:{rel.type.upper()}]->(m)
                """
                session.run(query, id=data.node.id, end_node_id=rel.end_node_id)

    def remove_node_and_relationships(self, node_id):
        with self.driver.session() as session:
            query = "MATCH (n) WHERE n.id=$id DETACH DELETE n"
            session.run(query, id=node_id)

    def get_node_label_by_id(self, node_id):
        with self.driver.session() as session:
            query = "MATCH (n) WHERE n.id = $id RETURN labels(n) AS labels"
            result = session.run(query, id=node_id)
            record = result.single()
            if record and record["labels"]:
                return record["labels"][0]
            return "User"
