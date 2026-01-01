from fastapi import FastAPI

from app.api.routers.user_router import router as user_router

app = FastAPI()

# routers
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
