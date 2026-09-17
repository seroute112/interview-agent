from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(title="Interview Agent API",version="0.1.0")
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Interview Agent API is running"}