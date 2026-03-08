from fastapi import FastAPI
from routers import auth, expenses, categories, accounts, recipients, voice

app = FastAPI(
    title="Expenses API",
    root_path="/api"
)

app.include_router(auth.router, tags=["auth"])
app.include_router(expenses.router, tags=["expenses"])
app.include_router(categories.router, tags=["categories"])
app.include_router(accounts.router, tags=["accounts"])
app.include_router(recipients.router, tags=["recipients"])
app.include_router(voice.router, tags=["voice"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
