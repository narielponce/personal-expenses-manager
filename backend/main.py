from fastapi import FastAPI
from routers import auth, expenses, categories, accounts, recipients

app = FastAPI()

app.include_router(auth.router, tags=["auth"])
app.include_router(expenses.router, tags=["expenses"])
app.include_router(categories.router, tags=["categories"])
app.include_router(accounts.router, tags=["accounts"])
app.include_router(recipients.router, tags=["recipients"])

@app.get("/")
def read_root():
    return {"Hello": "World"}
