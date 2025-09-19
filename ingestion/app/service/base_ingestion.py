from abc import ABC, abstractmethod
from app.schema.ingestion import IngestionType


# Ingestion Context
class IngestionContext:
    def __init__(self, ingestion_type: IngestionType, ingestion_source: str):
        self.ingestion_type = ingestion_type
        self.ingestion_source = ingestion_source


# BaseIngestion class to create any ingestion provider
class BaseIngestion(ABC):
    def __init__(self, ingestion_source: str):
        self.ingestion_source = ingestion_source

    # Extract data method to extract data using specific ingestion type
    @abstractmethod
    async def extract_and_ingest_data(self):
        pass
