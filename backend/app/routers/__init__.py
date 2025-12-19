from fastapi import APIRouter
from app.routers import (
    auth,
    users,
    admin,
    test,
    listening,
    reading,
    writing,
    speaking,
    grading,
    upload
)

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(test.router, prefix="/tests", tags=["Tests"])
api_router.include_router(listening.router, prefix="/listening", tags=["Listening"])
api_router.include_router(reading.router, prefix="/reading", tags=["Reading"])
api_router.include_router(writing.router, prefix="/writing", tags=["Writing"])
api_router.include_router(speaking.router, prefix="/speaking", tags=["Speaking"])
api_router.include_router(grading.router, prefix="/grading", tags=["Grading"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])

__all__ = ["api_router"]
