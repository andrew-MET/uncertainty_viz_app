from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.timeseries import router as timeseries_router
import traceback

app = FastAPI(title="Ensemble forecast API")

# Include routers
app.include_router(timeseries_router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
