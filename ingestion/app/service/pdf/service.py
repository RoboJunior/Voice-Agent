import os
import asyncio
from ..base_ingestion import BaseIngestion
from pypdf import PdfReader
import uuid
from app.service.qdrant_service import splitter, insert_documents
from colorama import Fore


# PdfIngestion Provider
class PdfIngestion(BaseIngestion):
    # Initalize the Pdf ingestion variables
    def __init__(self, ingestion_source: str):
        super().__init__(ingestion_source)

    # Extract and ingest data into vectordb
    async def extract_and_ingest_data(self):
        data = await self._extract_data(self.ingestion_source)
        tasks = [
            self._process_and_store_document(source, text) for source, text in data
        ]
        # Running all the tasks concurrently
        await asyncio.gather(*tasks)
        return {"message": "Successfully Ingested Pdf!"}

    # Split the text into chunks
    def _chunk_text(self, text: str):
        chunks = splitter.split_text(text)
        return chunks

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

    # Extract each page data
    def _extract_page(self, page, filename_withoutext: str, page_number: int):
        source_page = f"{filename_withoutext}_{page_number}.pdf"
        return (source_page, page.extract_text())

    # Extract the data sync
    async def _extract_data(self, filepath: str):
        reader = PdfReader(filepath)
        filename_withoutext = os.path.splitext(os.path.basename(filepath))[0]
        # Create async tasks for each page
        tasks = [
            asyncio.to_thread(self._extract_page, page, filename_withoutext, i + 1)
            for i, page in enumerate(reader.pages)
        ]
        # Run all page extractions concurrently
        return await asyncio.gather(*tasks)
