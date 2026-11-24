from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.database import Base, engine
from app.api import auth, upload, analysis

# Import models so metadata is registered before create_all
from app.models import user, file, analysis as analysis_model, forensic_signal  # noqa

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TruthLens AI",
    description="Multimodal Digital Authenticity & Fake Content Detection System",
    version="0.1.0",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Never leak raw stack traces to the client - spec section 62.
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "An unexpected error occurred while processing the request."},
    )


app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(analysis.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
