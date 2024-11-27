import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from models import InsertRequest, Node, Relationship
from dotenv import load_dotenv

load_dotenv()
auth_token = os.getenv('AUTH_TOKEN')

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def mock_neo4j_storage(monkeypatch):
    mock_storage = MagicMock()
    mock_storage.fetch_all_nodes.return_value = [
        {"id": 0, "label": "User"},
        {"id": 1, "label": "Group"},
        {"id": 2, "label": "User"}
    ]
    mock_storage.fetch_node_with_relationships.return_value = {
        "node": {"id": 0, "label": "User"},
        "relationships": [
            {"relationship_type": "FOLLOWS", "end_node_id": 2}
        ]
    }
    mock_storage.create_node_and_relationships.return_value = None
    mock_storage.remove_node_and_relationships.return_value = None
    app.state.db_handler = mock_storage
    return mock_storage

def test_get_all_nodes(client):
    response = client.get("/nodes")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 0, "label": "User"},
        {"id": 1, "label": "Group"},
        {"id": 2, "label": "User"}
    ]

def test_get_node_and_relationships(client):
    node_id = 0
    response = client.get(f"/node/{node_id}")
    assert response.status_code == 200
    assert response.json() == {
        "node": {"id": node_id, "label": "User"},
        "relationships": [
            {"relationship_type": "FOLLOWS", "end_node_id": 2}
        ]
    }

def test_add_node_and_relationships(client):
    node = Node(id=3, label="User", name="Дамир",  sex=2, city="Тюмень")
    relationships = [Relationship(type="FOLLOWS", end_node_id=2)]
    node_with_rels = InsertRequest(node=node, relationships=relationships)

    response = client.post("/node", json=node_with_rels.model_dump(), headers={"token": f"{auth_token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Node and its relationships added successfully"}

def test_delete_node_and_relationships(client):
    node_id = 3
    response = client.delete(f"/node/{node_id}", headers={"token": f"{auth_token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Node and its relationships deleted successfully"}

def test_verify_token_invalid(client):
    response = client.post("/node", headers={"token": "invalid_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}
