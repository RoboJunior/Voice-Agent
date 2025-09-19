import aiohttp
from app.config.settings import get_settings


# Search qdrant api call to ingestion service
async def search_qdrant_knowledgebase(query: str):
    params = {"query": query}
    async with aiohttp.ClientSession() as session:
        async with session.get(get_settings().SEARCH_URL, params=params) as response:
            return await response.json()
