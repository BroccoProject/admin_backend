from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.categories import router as categories_router
from api.routers.recipes import router as recipes_router

app = FastAPI(title="Brokulak Admin Panel API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories_router, prefix="/api/v1")
app.include_router(recipes_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
