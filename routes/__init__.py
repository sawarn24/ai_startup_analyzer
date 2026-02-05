"""
Routes Package
Export all routers for easy import
"""
from .health import router as health_router
from .documents import router as document_router
from .analysis import router as analysis_router
from .reports import router as report_router
from .email import router as email_router

__all__ = [
    'health_router',
    'document_router',
    'analysis_router',
    'report_router',
    'email_router'
]