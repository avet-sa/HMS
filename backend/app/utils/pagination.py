"""Pagination utilities for API endpoints"""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = 1
    page_size: int = 50
    
    def validate_params(self):
        """Ensure valid pagination parameters"""
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 10
        if self.page_size > 100:
            self.page_size = 100


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


def paginate(query: Query, page: int = 1, page_size: int = 50) -> dict:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Current page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary with items, total, page, page_size, total_pages
    """
    # Validate parameters
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    # Get total count
    total = query.count()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Get paginated items
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def apply_sorting(query: Query, model, sort_by: Optional[str] = None, sort_order: str = "asc") -> Query:
    """
    Apply sorting to a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        model: The SQLAlchemy model class
        sort_by: Field name to sort by
        sort_order: 'asc' or 'desc'
        
    Returns:
        Query with sorting applied
    """
    if not sort_by:
        return query
    
    # Validate sort order
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    
    # Check if field exists on model
    if hasattr(model, sort_by):
        field = getattr(model, sort_by)
        if sort_order.lower() == 'desc':
            query = query.order_by(field.desc())
        else:
            query = query.order_by(field.asc())
    
    return query
