from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from db import Neo4jStorage
from auth import verify_token
from models import InsertRequest
from dotenv import load_dotenv
import os

load_dotenv()

@asynccontextmanager
async def startup_shutdown(app: FastAPI):
    if not hasattr(app.state, "db_handler"):
        db_handler = Neo4jStorage(
            os.getenv("NEO4J_URL"),
            os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD")
        )
        app.state.db_handler = db_handler
    yield

    if hasattr(app.state, "db_handler"):
        app.state.db_handler.close()

app = FastAPI(lifespan=startup_shutdown)

@app.get("/nodes")
def get_all_nodes():
    return app.state.db_handler.fetch_all_nodes()

@app.get("/node/{node_id}")
def get_node_and_relationships(node_id: int):
    return app.state.db_handler.fetch_node_with_relationships(node_id)

@app.post("/node", dependencies=[Depends(verify_token)])
def add_node_and_relationships(node_data: InsertRequest):
    app.state.db_handler.create_node_and_relationships(node_data)
    return {"message": "Node and its relationships added successfully"}

@app.delete("/node/{node_id}", dependencies=[Depends(verify_token)])
def delete_node_and_relationships(node_id: int):
    app.state.db_handler.remove_node_and_relationships(node_id)
    return {"message": "Node and its relationships deleted successfully"}
