from fastapi import FastAPI
from app.api.api_endpoints import api_router_v1
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Adding middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# To check the health of the server
@app.get("/")
def server_health():
    return {"message": "Server successfully running in port 8000"}


app.include_router(api_router_v1, prefix="/v1")


# Running the server
def start_ingestion_service():
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=8000, reload=True)
