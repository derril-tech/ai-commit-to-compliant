"""
API v1 routes.
"""

from fastapi import APIRouter

from .endpoints import auth, projects, blueprints, runs, dashboards, pipelines, releases, enterprise

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(blueprints.router, prefix="/blueprints", tags=["blueprints"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["pipelines"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(releases.router, prefix="/releases", tags=["releases"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(enterprise.router, prefix="/enterprise", tags=["enterprise"])
