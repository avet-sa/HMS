"""
Service layer for Pricing Rules
"""
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..db.models import PricingRule, RoomType
from ..schemas.pricing_rule import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PriceCalculationRequest,
    PriceCalculationResponse,
)


class PricingRuleService:
    """Service for managing pricing rules and calculating prices"""
    
    @staticmethod
    def create_rule(db: Session, rule_data: PricingRuleCreate) -> PricingRule:
        """Create a new pricing rule"""
        rule = PricingRule(
            name=rule_data.name,
            description=rule_data.description,
            rule_type=rule_data.rule_type,  # Use string directly
            priority=rule_data.priority,
            adjustment_type=rule_data.adjustment_type,
            adjustment_value=rule_data.adjustment_value,
            room_type_id=rule_data.room_type_id,
            start_date=rule_data.start_date,
            end_date=rule_data.end_date,
            applicable_days=rule_data.applicable_days,
            min_nights=rule_data.min_nights,
            min_advance_days=rule_data.min_advance_days,
            max_advance_days=rule_data.max_advance_days,
            min_loyalty_tier=rule_data.min_loyalty_tier,
            is_active=rule_data.is_active,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def get_rule(db: Session, rule_id: int) -> Optional[PricingRule]:
        """Get a pricing rule by ID"""
        return db.query(PricingRule).filter(PricingRule.id == rule_id).first()
    
    @staticmethod
    def list_rules(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        rule_type: Optional[str] = None,
    ) -> List[PricingRule]:
        """List pricing rules with optional filters"""
        query = db.query(PricingRule)
        
        if is_active is not None:
            query = query.filter(PricingRule.is_active == is_active)
        
        if rule_type:
            query = query.filter(PricingRule.rule_type == rule_type)
        
        # Order by priority (descending) and created_at
        query = query.order_by(PricingRule.priority.desc(), PricingRule.created_at.desc())
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_rule(
        db: Session,
        rule_id: int,
        rule_data: PricingRuleUpdate,
    ) -> Optional[PricingRule]:
        """Update a pricing rule"""
        rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
        if not rule:
            return None
        
        update_data = rule_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(rule, key, value)
        
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def delete_rule(db: Session, rule_id: int) -> bool:
        """Delete a pricing rule"""
        rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
        if not rule:
            return False
        
        db.delete(rule)
        db.commit()
        return True
    
    @staticmethod
    def calculate_price(
        db: Session,
        calc_request: PriceCalculationRequest,
    ) -> PriceCalculationResponse:
        """
        Calculate price with all applicable pricing rules
        
        Rules are applied in order of priority (highest first).
        Multiple rules can be applied cumulatively.
        """
        # Get base price
        if calc_request.base_price:
            base_price = calc_request.base_price
        else:
            room_type = db.query(RoomType).filter(RoomType.id == calc_request.room_type_id).first()
            if not room_type:
                raise ValueError(f"Room type {calc_request.room_type_id} not found")
            base_price = room_type.base_price
        
        # Calculate nights
        total_nights = (calc_request.check_out - calc_request.check_in).days
        if total_nights <= 0:
            raise ValueError("Check-out must be after check-in")
        
        # Get applicable rules
        applicable_rules = PricingRuleService._get_applicable_rules(
            db=db,
            room_type_id=calc_request.room_type_id,
            check_in=calc_request.check_in,
            check_out=calc_request.check_out,
            total_nights=total_nights,
            loyalty_tier=calc_request.guest_loyalty_tier,
        )
        
        # Apply rules
        adjusted_price = base_price
        applied_rules_details = []
        
        for rule in applicable_rules:
            old_price = adjusted_price
            
            if rule.adjustment_type == "percentage":
                adjustment = adjusted_price * (rule.adjustment_value / 100)
                adjusted_price += adjustment
            else:  # fixed_amount
                adjusted_price += rule.adjustment_value
            
            # Ensure price doesn't go negative
            adjusted_price = max(Decimal("0.00"), adjusted_price)
            
            applied_rules_details.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "rule_type": rule.rule_type,  # Already a string
                "adjustment_type": rule.adjustment_type,
                "adjustment_value": float(rule.adjustment_value),
                "price_before": float(old_price),
                "price_after": float(adjusted_price),
            })
        
        total_price = adjusted_price * total_nights
        base_total = base_price * total_nights
        savings = base_total - total_price
        
        return PriceCalculationResponse(
            base_price=base_price,
            total_nights=total_nights,
            applied_rules=applied_rules_details,
            adjusted_price_per_night=adjusted_price,
            total_price=total_price,
            savings=savings,
        )
    
    @staticmethod
    def _get_applicable_rules(
        db: Session,
        room_type_id: int,
        check_in: date,
        check_out: date,
        total_nights: int,
        loyalty_tier: int,
    ) -> List[PricingRule]:
        """Get all applicable pricing rules for the given booking parameters"""
        today = date.today()
        days_until_checkin = (check_in - today).days
        
        # Query active rules, ordered by priority (descending)
        query = db.query(PricingRule).filter(PricingRule.is_active == True)
        
        # Filter by room type (NULL means applies to all room types)
        query = query.filter(
            or_(
                PricingRule.room_type_id == room_type_id,
                PricingRule.room_type_id.is_(None)
            )
        )
        
        # Filter by date range (if specified)
        query = query.filter(
            or_(
                and_(
                    PricingRule.start_date.is_(None),
                    PricingRule.end_date.is_(None)
                ),
                and_(
                    PricingRule.start_date <= check_in,
                    PricingRule.end_date >= check_in
                ),
                and_(
                    PricingRule.start_date.is_(None),
                    PricingRule.end_date >= check_in
                ),
                and_(
                    PricingRule.start_date <= check_in,
                    PricingRule.end_date.is_(None)
                ),
            )
        )
        
        # Order by priority
        query = query.order_by(PricingRule.priority.desc())
        
        rules = query.all()
        
        # Further filter rules based on conditions
        applicable_rules = []
        
        for rule in rules:
            # Check minimum nights
            if rule.min_nights and total_nights < rule.min_nights:
                continue
            
            # Check advance booking days
            if rule.min_advance_days and days_until_checkin < rule.min_advance_days:
                continue
            
            if rule.max_advance_days and days_until_checkin > rule.max_advance_days:
                continue
            
            # Check loyalty tier
            if rule.min_loyalty_tier and loyalty_tier < rule.min_loyalty_tier:
                continue
            
            # Check applicable days of week
            if rule.applicable_days:
                try:
                    applicable_days = json.loads(rule.applicable_days)
                    # Check if any night of the stay falls on an applicable day
                    applicable = False
                    for i in range(total_nights):
                        night_date = check_in + timedelta(days=i)
                        if night_date.weekday() in applicable_days:
                            applicable = True
                            break
                    if not applicable:
                        continue
                except (json.JSONDecodeError, TypeError):
                    # Invalid JSON, skip this check
                    pass
            
            applicable_rules.append(rule)
        
        return applicable_rules
