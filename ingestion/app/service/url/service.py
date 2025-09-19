from ..base_ingestion import BaseIngestion
from crawl4ai import AsyncWebCrawler
from app.service.qdrant_service import splitter, insert_documents
import asyncio
from colorama import Fore
import uuid


# Url Ingestion Provider
class UrlIngestion(BaseIngestion):
    # Initalize the Url ingestion variables
    def __init__(self, ingestion_source: str):
        super().__init__(ingestion_source)

    # Extract the ingest the url content to the vectordb
    async def extract_and_ingest_data(self):
        data = await self._extract_data(self.ingestion_source)
        await self._process_and_store_document(source=self.ingestion_source, text=data)
        return {"message": "Successfully Ingested Url!"}

    # Process and store the chunked documents to vector db
    async def _process_and_store_document(self, source: str, text: str):
        """Process a document and store its chunks in parallel."""
        chunks = await asyncio.to_thread(self._chunk_text, text)
        docs = [
            {"text": chunk, "source": source, "id": str(uuid.uuid4())}
            for chunk in chunks
        ]
        print(Fore.CYAN + f"Processing source : {source}")
        await insert_documents(docs=docs)

    # Split the text into chunks
    def _chunk_text(self, text: str):
        chunks = splitter.split_text(text)
        return chunks

    # Extract the markdown from the given url
    async def _extract_data(self, url_source: str):
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url_source,
            )
        return result.markdown
