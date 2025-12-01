from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.routers import automations, auth

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(automations.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "AutoISP API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
