from fastapi import APIRouter
from app.api.v1 import auth, code, reviews, findings, tests, dashboard

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(code.router)
api_router.include_router(reviews.router)
api_router.include_router(findings.router)
api_router.include_router(tests.router)
api_router.include_router(dashboard.router)
