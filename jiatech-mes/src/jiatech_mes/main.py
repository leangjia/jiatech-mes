"""Jia Tech MES Application.

This module provides the main FastAPI application for Jia Tech MES.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jiatech_mes.api import mes_router
from jiatech_mes.orm.registry import get_default_registry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    _logger.info("Starting Jia Tech MES Application")
    
    registry = get_default_registry()
    _logger.info(f"Registry initialized with {len(registry.models)} models")
    
    yield
    
    _logger.info("Shutting down Jia Tech MES Application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title='Jia Tech MES API',
        description='Manufacturing Execution System REST API',
        version='1.0.0',
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    
    app.include_router(mes_router)
    
    @app.get('/')
    async def root():
        return {
            'name': 'Jia Tech MES API',
            'version': '1.0.0',
            'status': 'running',
        }
    
    return app


app = create_app()
