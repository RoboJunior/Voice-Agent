from fastapi import APIRouter
from .endpoints import ingest

api_router_v1 = APIRouter()
# Adding all the routers here
api_router_v1.include_router(ingest.ingestion_router, prefix="/ingest", tags=["Ingest"])
