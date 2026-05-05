from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .routers import auth, draw, donation
from .database import engine, Base

# Init DB schema
Base.metadata.create_all(bind=engine)

app = FastAPI(title="宮廟抽籤系統 API")

# Register routers
app.include_router(auth.router)
app.include_router(draw.router)
app.include_router(donation.router)

# Ensure frontend dir exists for mounting
os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_index():
    index_path = "frontend/index.html"
    if not os.path.exists(index_path):
        return HTMLResponse(content="Frontend missing")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
