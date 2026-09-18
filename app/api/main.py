from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import router


app = FastAPI(title="Interview Agent API",version="0.1.0")
app.include_router(router)

@app.exception_handler(Exception)
async def global_exception_handler(request,exc):
    return JSONResponse(
        status_code = 500,
        content = {"detail":f"服务器内部错误:{str(exc)}"},
    )

@app.get("/")
def root():
    return {"message": "Interview Agent API is running"}