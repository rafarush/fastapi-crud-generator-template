from fastapi import FastAPI

from app.api.routers import user_router

app = FastAPI()

# routers
app.include_router(user_router.router, prefix='/user', tags=['user'])


@app.get("/")
async def root():
    return {"message": "Hello World"}
