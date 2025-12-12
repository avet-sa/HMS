"""
API endpoints for Pricing Rules
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..schemas.pricing_rule import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PricingRuleResponse,
    PriceCalculationRequest,
    PriceCalculationResponse,
)
from ..services.pricing_rule_service import PricingRuleService
from ..dependencies.security import get_current_user, require_role
from ..db.models import User, PermissionLevel
from ..utils.audit import log_audit

router = APIRouter(prefix="/pricing-rules", tags=["Pricing Rules"])


@router.post("/", response_model=PricingRuleResponse, status_code=201)
def create_pricing_rule(
    rule_data: PricingRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN)),
):
    """
    Create a new pricing rule
    
    Requires MANAGER or ADMIN permission
    """
    try:
        rule = PricingRuleService.create_rule(db, rule_data)
        
        # Audit log
        log_audit(
            db=db,
            user=current_user,
            action="CREATE",
            entity_type="pricing_rule",
            entity_id=rule.id,
            description=f"Created pricing rule: {rule.name}",
            new_values={"rule_data": str(rule_data.model_dump())},
        )
        
        return rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PricingRuleResponse])
def list_pricing_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    rule_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all pricing rules with optional filters
    
    Filters:
    - is_active: Filter by active status
    - rule_type: Filter by rule type (seasonal, weekend, early_bird, etc.)
    """
    rules = PricingRuleService.list_rules(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        rule_type=rule_type,
    )
    return rules


@router.get("/{rule_id}", response_model=PricingRuleResponse)
def get_pricing_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific pricing rule by ID"""
    rule = PricingRuleService.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    return rule


@router.patch("/{rule_id}", response_model=PricingRuleResponse)
def update_pricing_rule(
    rule_id: int,
    rule_data: PricingRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PermissionLevel.MANAGER, PermissionLevel.ADMIN)),
):
    """
    Update a pricing rule
    
    Requires MANAGER or ADMIN permission
    """
    rule = PricingRuleService.update_rule(db, rule_id, rule_data)
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    # Audit log
    log_audit(
        db=db,
        user=current_user,
        action="UPDATE",
        entity_type="pricing_rule",
        entity_id=rule.id,
        description=f"Updated pricing rule: {rule.name}",
        new_values={"updates": str(rule_data.model_dump(exclude_unset=True))},
    )
    
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_pricing_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(PermissionLevel.ADMIN)),
):
    """
    Delete a pricing rule
    
    Requires ADMIN permission
    """
    rule = PricingRuleService.get_rule(db, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    success = PricingRuleService.delete_rule(db, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    # Audit log
    log_audit(
        db=db,
        user=current_user,
        action="DELETE",
        entity_type="pricing_rule",
        entity_id=rule_id,
        description=f"Deleted pricing rule: {rule.name}",
    )
    
    return None


@router.post("/calculate-price", response_model=PriceCalculationResponse)
def calculate_price(
    calc_request: PriceCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate price for a booking with all applicable pricing rules
    
    This endpoint applies all active pricing rules that match the criteria:
    - Room type
    - Check-in/check-out dates
    - Guest loyalty tier
    - Advance booking days
    - Length of stay
    
    Returns the adjusted price with details of all applied rules.
    """
    try:
        result = PricingRuleService.calculate_price(db, calc_request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
