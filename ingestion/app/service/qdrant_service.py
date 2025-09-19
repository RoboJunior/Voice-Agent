import asyncio
from qdrant_client import AsyncQdrantClient
from app.config.settings import get_settings
from contextlib import asynccontextmanager
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from fastembed import TextEmbedding
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http import models
import sys
from typing import List

# Intialzing the text and the image embedding models
text_model = TextEmbedding(get_settings().TEXT_EMBEDDING_MODEL_NAME)

emb = HuggingFaceEmbeddings(
    model_name=get_settings().TEXT_EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
# Initalizing the semantic text splitter
splitter = SemanticChunker(embeddings=emb)


# Intializing the qdrant client
@asynccontextmanager
async def get_qdrant_client():
    client = AsyncQdrantClient(
        url=get_settings().QDRANT_URL, api_key=get_settings().QDRANT_API_KEY
    )
    try:
        yield client
    finally:
        await client.close()


# Create new collection
async def create_new_collection(collection_name: str):
    async with get_qdrant_client() as client:
        exits = await client.collection_exists(collection_name=collection_name)
        if not exits:
            await client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "text": VectorParams(
                        size=text_model.embedding_size, distance=Distance.COSINE
                    )
                },
            )
            print("New collection created with collection name: ", collection_name)
        else:
            print("Collection already exists !")


# Insert documents into qdrantvectordb
async def insert_documents(docs: List[dict]):
    # Run embeddings concurrently
    tasks = [asyncio.to_thread(text_model.embed, [doc["text"]]) for doc in docs]
    embeddings = await asyncio.gather(*tasks)

    points = []
    for doc, emb in zip(docs, embeddings):
        txt_emb = list(emb)[0]
        points.append(
            models.PointStruct(
                id=doc["id"],
                vector={"text": txt_emb},
                payload={"text": doc["text"], "source": doc["source"]},
            )
        )
    async with get_qdrant_client() as client:
        client.upload_points(
            collection_name=get_settings().COLLECTION_NAME, points=points
        )


# Search the user query in the knowledge base
async def search_query(content: str):
    txt_emb = list(text_model.embed([content]))[0]
    async with get_qdrant_client() as client:
        res = await client.search(
            collection_name=get_settings().COLLECTION_NAME,
            query_vector=("text", txt_emb),
            with_payload=["url", "text"],
            limit=5,
        )
        print(res)
        return res


# Poetry run statement to create a new qdrant collection
def create_new_qdrant_collection():
    collection_name = sys.argv[1]
    asyncio.run(create_new_collection(collection_name=collection_name))
