from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routers import auth, expenses, categories, accounts, recipients, voice, backup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Expenses API",
    root_path="/api"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )

app.include_router(auth.router, tags=["auth"])
app.include_router(expenses.router, tags=["expenses"])
app.include_router(categories.router, tags=["categories"])
app.include_router(accounts.router, tags=["accounts"])
app.include_router(recipients.router, tags=["recipients"])
app.include_router(voice.router, tags=["voice"])
app.include_router(backup.router, prefix="/backup", tags=["backup"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
