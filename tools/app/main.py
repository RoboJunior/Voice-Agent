from fastmcp import FastMCP
from app.api.ingestion_api import search_qdrant_knowledgebase
from fastmcp.utilities.logging import get_logger

mcp = FastMCP("Voice Agent Mcp Server")

# Intailzing the mcp logge
logger = get_logger(__name__)


# Tool to query from the ingested knowledge base
@mcp.tool(
    name="knowledge_search",
    title="Qdrant Knowleadge Search Tool",
    description="This tools is used to perform knowledge search",
)
async def qdrant_knowledge_search(query: str):
    try:
        logger.info(f"Searching Query in Knowledge Base: {query}")
        results = await search_qdrant_knowledgebase(query=query)
        logger.info(f"Search Results Found : {results}")
        logger.info(f"Number of relevant results found: {len(results)}")
        return results
    except Exception as e:
        logger.error(f"Reterival failed: {str(e)}")


# Poetry run command to start the mcp server
def start_mcp_server():
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8005)
