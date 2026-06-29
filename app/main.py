from fastapi import FastAPI, status

from .core import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    )

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        }
