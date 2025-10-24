from fastapi import FastAPI
from dotenv import load_dotenv
from api.routes.receipt import router as receipt_router

load_dotenv()

app = FastAPI(title="Receipt Splitter API")

# Include routers
app.include_router(receipt_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
