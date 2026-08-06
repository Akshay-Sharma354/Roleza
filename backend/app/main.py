from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.browser import router as browser_router

app = FastAPI(title="Roleza API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(browser_router)


@app.get("/")
def home():
    return {"message": "Welcome to Roleza 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}