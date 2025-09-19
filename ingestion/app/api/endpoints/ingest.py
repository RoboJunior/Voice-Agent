from fastapi import HTTPException, APIRouter
from app.utils.comman_utilis import validate_url
from app.service.ingestion_factory import IngestionFactory
from app.service.base_ingestion import IngestionContext
from app.schema.ingestion import IngestionType
from app.service.qdrant_service import search_query

# Initalizing the app
ingestion_router = APIRouter()


# Api to ingest the given data
@ingestion_router.post("/ingest_data")
async def ingest_url_pdf(input_source: str):
    ingestion_factory = IngestionFactory()
    # Ingest pdf logic
    if input_source.endswith(".pdf"):
        pdf = ingestion_factory.create_ingestion_type(
            IngestionContext(
                ingestion_type=IngestionType.PDF, ingestion_source=input_source
            )
        )
        return await pdf.extract_and_ingest_data()
    elif await validate_url(url_string=input_source):
        # Inget the url logic
        url = ingestion_factory.create_ingestion_type(
            IngestionContext(
                ingestion_type=IngestionType.URL, ingestion_source=input_source
            )
        )
        return await url.extract_and_ingest_data()
    else:
        raise HTTPException(status_code=403, detail="File format not allowed/supported")


@ingestion_router.get("/search")
async def search_vector_db(query: str):
    # Search the query in knowledge base
    return await search_query(content=query)
