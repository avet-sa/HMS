"""
Pydantic schemas for Pricing Rules
"""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class PricingRuleBase(BaseModel):
    """Base schema for pricing rule"""
    name: str
    description: Optional[str] = None
    rule_type: str  # seasonal, weekend, early_bird, last_minute, loyalty, long_stay, custom
    priority: int = 0
    adjustment_type: str  # percentage, fixed_amount
    adjustment_value: Decimal
    room_type_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    applicable_days: Optional[str] = None  # JSON string of day numbers [0-6]
    min_nights: Optional[int] = None
    min_advance_days: Optional[int] = None
    max_advance_days: Optional[int] = None
    min_loyalty_tier: Optional[int] = None
    is_active: bool = True
    
    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v: str) -> str:
        valid_types = ["seasonal", "weekend", "early_bird", "last_minute", "loyalty", "long_stay", "custom"]
        if v not in valid_types:
            raise ValueError(f"rule_type must be one of {valid_types}")
        return v
    
    @field_validator("adjustment_type")
    @classmethod
    def validate_adjustment_type(cls, v: str) -> str:
        if v not in ["percentage", "fixed_amount"]:
            raise ValueError("adjustment_type must be 'percentage' or 'fixed_amount'")
        return v
    
    @field_validator("adjustment_value")
    @classmethod
    def validate_adjustment_value(cls, v: Decimal, info) -> Decimal:
        adjustment_type = info.data.get("adjustment_type")
        if adjustment_type == "percentage":
            if v < -100 or v > 100:
                raise ValueError("percentage adjustment must be between -100 and 100")
        return v


class PricingRuleCreate(PricingRuleBase):
    """Schema for creating a pricing rule"""
    pass


class PricingRuleUpdate(BaseModel):
    """Schema for updating a pricing rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    priority: Optional[int] = None
    adjustment_type: Optional[str] = None
    adjustment_value: Optional[Decimal] = None
    room_type_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    applicable_days: Optional[str] = None
    min_nights: Optional[int] = None
    min_advance_days: Optional[int] = None
    max_advance_days: Optional[int] = None
    min_loyalty_tier: Optional[int] = None
    is_active: Optional[bool] = None


class PricingRuleResponse(PricingRuleBase):
    """Schema for pricing rule response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class PriceCalculationRequest(BaseModel):
    """Request schema for calculating price with rules"""
    room_type_id: int
    check_in: date
    check_out: date
    guest_loyalty_tier: int = 0
    base_price: Optional[Decimal] = None  # If not provided, uses room_type base_price


class PriceCalculationResponse(BaseModel):
    """Response schema for price calculation"""
    base_price: Decimal
    total_nights: int
    applied_rules: List[dict]  # List of applied rule details
    adjusted_price_per_night: Decimal
    total_price: Decimal
    savings: Decimal  # Amount saved from rules
    
    model_config = ConfigDict(from_attributes=True)
