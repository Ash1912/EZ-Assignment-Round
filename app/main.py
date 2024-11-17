from fastapi import FastAPI
from app.routers import ops_user, client_user

app = FastAPI(
    title="Secure File Sharing System",
    description="A secure platform for file sharing between Ops Users and Client Users",
    version="1.0.0",
)

# Include Routers
app.include_router(ops_user.router)
app.include_router(client_user.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Secure File Sharing System!"}
