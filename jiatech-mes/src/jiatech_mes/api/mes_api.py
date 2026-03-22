"""Jia Tech MES Web API Module.

This module provides FastAPI-based REST API endpoints for MES operations.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime

from jiatech_mes.orm import registry as registry_module
from jiatech_mes.orm.registry import Registry, get_default_registry

router = APIRouter(prefix='/api/v1', tags=['mes'])


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    models: int


@router.get('/health', response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health status."""
    reg = get_default_registry()
    return HealthResponse(
        status='ok',
        timestamp=datetime.now().isoformat(),
        models=len(reg.models) if reg else 0,
    )


class ModelInfoResponse(BaseModel):
    name: str
    description: str
    fields: dict[str, Any]


@router.get('/models', response_model=list[ModelInfoResponse])
async def list_models() -> list[ModelInfoResponse]:
    """List all registered models."""
    reg = get_default_registry()
    result = []
    
    for model_name in reg.models:
        model_class = reg[model_name]
        result.append(ModelInfoResponse(
            name=model_name,
            description=model_class._description or '',
            fields={},
        ))
    
    return result


@router.get('/models/{model_name}', response_model=ModelInfoResponse)
async def get_model_info(model_name: str) -> ModelInfoResponse:
    """Get model information."""
    reg = get_default_registry()
    
    if model_name not in reg:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
    
    model_class = reg[model_name]
    fields_info = {}
    
    for field_name, field in model_class._fields.items():
        fields_info[field_name] = {
            'type': getattr(field, '_type', 'unknown'),
            'string': getattr(field, 'string', ''),
            'required': getattr(field, 'required', False),
        }
    
    return ModelInfoResponse(
        name=model_name,
        description=model_class._description or '',
        fields=fields_info,
    )


class SearchRequest(BaseModel):
    domain: list = Field(default_factory=list)
    offset: int = 0
    limit: int | None = 100
    order: str | None = None


class RecordResponse(BaseModel):
    id: int
    data: dict[str, Any]


class SearchResponse(BaseModel):
    records: list[RecordResponse]
    total: int


@router.post('/models/{model_name}/search', response_model=SearchResponse)
async def search_records(
    model_name: str,
    request: SearchRequest,
) -> SearchResponse:
    """Search for records."""
    reg = get_default_registry()
    
    if model_name not in reg:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
    
    return SearchResponse(
        records=[],
        total=0,
    )


class CreateRequest(BaseModel):
    data: dict[str, Any]


class CreateResponse(BaseModel):
    id: int


@router.post('/models/{model_name}', response_model=CreateResponse)
async def create_record(
    model_name: str,
    request: CreateRequest,
) -> CreateResponse:
    """Create a new record."""
    reg = get_default_registry()
    
    if model_name not in reg:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
    
    return CreateResponse(id=0)


class UpdateRequest(BaseModel):
    ids: list[int]
    data: dict[str, Any]


class UpdateResponse(BaseModel):
    success: bool
    updated: int


@router.put('/models/{model_name}', response_model=UpdateResponse)
async def update_records(
    model_name: str,
    request: UpdateRequest,
) -> UpdateResponse:
    """Update records."""
    reg = get_default_registry()
    
    if model_name not in reg:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
    
    return UpdateResponse(success=True, updated=0)


class DeleteRequest(BaseModel):
    ids: list[int]


class DeleteResponse(BaseModel):
    success: bool
    deleted: int


@router.delete('/models/{model_name}', response_model=DeleteResponse)
async def delete_records(
    model_name: str,
    request: DeleteRequest,
) -> DeleteResponse:
    """Delete records."""
    reg = get_default_registry()
    
    if model_name not in reg:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_name}")
    
    return DeleteResponse(success=True, deleted=0)


mes_router = router
