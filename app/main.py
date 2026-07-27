from fastapi import FastAPI

app = FastAPI(
    title="Cloud File Storage Service",
    description="REST API for secure file upload, download, and metadata management.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy"}