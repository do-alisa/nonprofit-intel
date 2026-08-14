from fastapi import FastAPI

app = FastAPI(title="Nonprofit Intelligence API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}