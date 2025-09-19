from app.service.pdf.service import PdfIngestion
from app.service.url.service import UrlIngestion
from app.service.base_ingestion import IngestionContext
from app.schema.ingestion import IngestionType


# Creating the ingestion factory Dynamically
# Creating a new ingestion context would require no work it would be easily handled
# As here we have used the factory desgin pattern to add new ingestion without breaking the exiting functionality
class IngestionFactory:
    @staticmethod
    def create_ingestion_type(ingest_context: IngestionContext):
        # Initalize the pdf ingestion class
        if ingest_context.ingestion_type == IngestionType.PDF:
            return PdfIngestion(ingestion_source=ingest_context.ingestion_source)
        # Initalize the url ingestion class
        elif ingest_context.ingestion_type == IngestionType.URL:
            return UrlIngestion(ingestion_source=ingest_context.ingestion_source)
        # Raise a Error if a invalid format is provided
        else:
            raise ValueError("Invalid ingestion type provided")
