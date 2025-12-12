"""
Tests for Pricing Rules functionality
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from backend.app.schemas.pricing_rule import PricingRuleCreate, PriceCalculationRequest
from backend.app.services.pricing_rule_service import PricingRuleService
from backend.app.db.models import RoomType, PricingRule


@pytest.fixture
def room_type(db):
    """Create a test room type"""
    room_type = RoomType(
        name="Deluxe Suite",
        base_price=Decimal("100.00"),
        capacity=2,
        description="Luxury room"
    )
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


def test_create_pricing_rule(client, admin_headers, db):
    """Test creating a pricing rule"""
    response = client.post(
        "/pricing-rules/",
        headers=admin_headers,
        json={
            "name": "Weekend Premium",
            "description": "Higher rates for weekends",
            "rule_type": "weekend",
            "priority": 10,
            "adjustment_type": "percentage",
            "adjustment_value": 20.0,
            "applicable_days": "[5, 6]",  # Saturday and Sunday
            "is_active": True
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Weekend Premium"
    assert data["rule_type"] == "weekend"
    assert data["adjustment_value"] == "20.00"


def test_list_pricing_rules(client, admin_headers, db):
    """Test listing pricing rules"""
    # Create test rules
    rule1 = PricingRule(
        name="Rule 1",
        rule_type="seasonal",
        priority=5,
        adjustment_type="percentage",
        adjustment_value=10,
        is_active=True
    )
    rule2 = PricingRule(
        name="Rule 2",
        rule_type="weekend",
        priority=8,
        adjustment_type="percentage",
        adjustment_value=15,
        is_active=False
    )
    db.add_all([rule1, rule2])
    db.commit()
    
    # List all rules
    response = client.get(
        "/pricing-rules/",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    
    # Filter by active status
    response = client.get(
        "/pricing-rules/?is_active=true",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(rule["is_active"] for rule in data)


def test_get_pricing_rule(client, admin_headers, db):
    """Test getting a specific pricing rule"""
    rule = PricingRule(
        name="Test Rule",
        rule_type="early_bird",
        priority=5,
        adjustment_type="percentage",
        adjustment_value=-15,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    response = client.get(
        f"/pricing-rules/{rule.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rule.id
    assert data["name"] == "Test Rule"


def test_update_pricing_rule(client, admin_headers, db):
    """Test updating a pricing rule"""
    rule = PricingRule(
        name="Old Name",
        rule_type="seasonal",
        priority=5,
        adjustment_type="percentage",
        adjustment_value=10,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    response = client.patch(
        f"/pricing-rules/{rule.id}",
        headers=admin_headers,
        json={
            "name": "New Name",
            "adjustment_value": 15.0,
            "is_active": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["adjustment_value"] == "15.00"
    assert data["is_active"] is False


def test_delete_pricing_rule(client, admin_headers, db):
    """Test deleting a pricing rule"""
    rule = PricingRule(
        name="To Delete",
        rule_type="custom",
        priority=1,
        adjustment_type="percentage",
        adjustment_value=5,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    response = client.delete(
        f"/pricing-rules/{rule.id}",
        headers=admin_headers
    )
    
    assert response.status_code == 204
    
    # Verify it's deleted
    response = client.get(
        f"/pricing-rules/{rule.id}",
        headers=admin_headers
    )
    assert response.status_code == 404


def test_calculate_price_no_rules(db, room_type):
    """Test price calculation with no rules applied"""
    today = date.today()
    check_in = today + timedelta(days=7)
    check_out = check_in + timedelta(days=3)
    
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    
    result = PricingRuleService.calculate_price(db, calc_request)
    
    assert result.base_price == Decimal("100.00")
    assert result.total_nights == 3
    assert result.adjusted_price_per_night == Decimal("100.00")
    assert result.total_price == Decimal("300.00")
    assert result.savings == Decimal("0.00")
    assert len(result.applied_rules) == 0


def test_calculate_price_with_percentage_discount(db, room_type):
    """Test price calculation with percentage discount"""
    # Create early bird discount rule
    rule = PricingRule(
        name="Early Bird 15%",
        rule_type="early_bird",
        priority=5,
        adjustment_type="percentage",
        adjustment_value=-15,  # 15% discount
        min_advance_days=30,
        is_active=True
    )
    db.add(rule)
    db.commit()
    
    # Book 45 days in advance
    today = date.today()
    check_in = today + timedelta(days=45)
    check_out = check_in + timedelta(days=2)
    
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    
    result = PricingRuleService.calculate_price(db, calc_request)
    
    assert result.base_price == Decimal("100.00")
    assert result.total_nights == 2
    assert result.adjusted_price_per_night == Decimal("85.00")  # 100 - 15%
    assert result.total_price == Decimal("170.00")  # 85 * 2
    assert result.savings == Decimal("30.00")  # (100 - 85) * 2
    assert len(result.applied_rules) == 1
    assert result.applied_rules[0]["rule_name"] == "Early Bird 15%"


def test_calculate_price_with_weekend_premium(db, room_type):
    """Test price calculation with weekend premium"""
    # Create weekend premium rule (Friday and Saturday = days 4 and 5)
    rule = PricingRule(
        name="Weekend +20%",
        rule_type="weekend",
        priority=10,
        adjustment_type="percentage",
        adjustment_value=20,  # 20% increase
        applicable_days="[4, 5]",  # Friday and Saturday
        is_active=True
    )
    db.add(rule)
    db.commit()
    
    # Find next Friday
    today = date.today()
    days_until_friday = (4 - today.weekday()) % 7
    if days_until_friday == 0:
        days_until_friday = 7
    check_in = today + timedelta(days=days_until_friday)
    check_out = check_in + timedelta(days=2)  # Friday to Sunday
    
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    
    result = PricingRuleService.calculate_price(db, calc_request)
    
    assert result.adjusted_price_per_night == Decimal("120.00")  # 100 + 20%
    assert len(result.applied_rules) == 1


def test_calculate_price_with_long_stay_discount(db, room_type):
    """Test price calculation with long stay discount"""
    rule = PricingRule(
        name="Long Stay 10%",
        rule_type="long_stay",
        priority=8,
        adjustment_type="percentage",
        adjustment_value=-10,
        min_nights=7,
        is_active=True
    )
    db.add(rule)
    db.commit()
    
    today = date.today()
    check_in = today + timedelta(days=14)
    check_out = check_in + timedelta(days=7)  # 7 nights
    
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    
    result = PricingRuleService.calculate_price(db, calc_request)
    
    assert result.adjusted_price_per_night == Decimal("90.00")  # 100 - 10%
    assert result.total_price == Decimal("630.00")  # 90 * 7
    assert len(result.applied_rules) == 1


def test_calculate_price_with_multiple_rules(db, room_type):
    """Test price calculation with multiple stacked rules"""
    # Create multiple rules
    rule1 = PricingRule(
        name="Early Bird 10%",
        rule_type="early_bird",
        priority=10,
        adjustment_type="percentage",
        adjustment_value=-10,
        min_advance_days=30,
        is_active=True
    )
    rule2 = PricingRule(
        name="Long Stay 5%",
        rule_type="long_stay",
        priority=5,
        adjustment_type="percentage",
        adjustment_value=-5,
        min_nights=5,
        is_active=True
    )
    db.add_all([rule1, rule2])
    db.commit()
    
    # Book 45 days in advance for 5 nights
    today = date.today()
    check_in = today + timedelta(days=45)
    check_out = check_in + timedelta(days=5)
    
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    
    result = PricingRuleService.calculate_price(db, calc_request)
    
    # First apply early bird: 100 - 10% = 90
    # Then apply long stay: 90 - 5% = 85.5
    assert result.adjusted_price_per_night == Decimal("85.50")
    assert result.total_price == Decimal("427.50")  # 85.5 * 5
    assert len(result.applied_rules) == 2


def test_calculate_price_with_loyalty_tier(db, room_type):
    """Test price calculation with loyalty tier requirement"""
    rule = PricingRule(
        name="VIP Discount",
        rule_type="loyalty",
        priority=7,
        adjustment_type="percentage",
        adjustment_value=-20,
        min_loyalty_tier=2,
        is_active=True
    )
    db.add(rule)
    db.commit()
    
    today = date.today()
    check_in = today + timedelta(days=10)
    check_out = check_in + timedelta(days=2)
    
    # Regular guest (tier 0) - should not get discount
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    result = PricingRuleService.calculate_price(db, calc_request)
    assert result.adjusted_price_per_night == Decimal("100.00")
    assert len(result.applied_rules) == 0
    
    # VIP guest (tier 2) - should get discount
    calc_request.guest_loyalty_tier = 2
    result = PricingRuleService.calculate_price(db, calc_request)
    assert result.adjusted_price_per_night == Decimal("80.00")  # 100 - 20%
    assert len(result.applied_rules) == 1


def test_calculate_price_with_date_range(db, room_type):
    """Test price calculation with date range restrictions"""
    # Summer season pricing (June 1 to August 31)
    rule = PricingRule(
        name="Summer Season",
        rule_type="seasonal",
        priority=9,
        adjustment_type="percentage",
        adjustment_value=25,  # 25% increase
        start_date=date(date.today().year, 6, 1),
        end_date=date(date.today().year, 8, 31),
        is_active=True
    )
    db.add(rule)
    db.commit()
    
    # Book in July (should apply)
    check_in = date(date.today().year, 7, 15)
    check_out = check_in + timedelta(days=2)
    
    calc_request = PriceCalculationRequest(
        room_type_id=room_type.id,
        check_in=check_in,
        check_out=check_out,
        guest_loyalty_tier=0
    )
    result = PricingRuleService.calculate_price(db, calc_request)
    assert result.adjusted_price_per_night == Decimal("125.00")  # 100 + 25%
    
    # Book in December (should not apply)
    check_in = date(date.today().year, 12, 15)
    check_out = check_in + timedelta(days=2)
    
    calc_request.check_in = check_in
    calc_request.check_out = check_out
    result = PricingRuleService.calculate_price(db, calc_request)
    assert result.adjusted_price_per_night == Decimal("100.00")


def test_calculate_price_permission_required(client, regular_headers):
    """Test that price calculation requires authentication"""
    response = client.post(
        "/pricing-rules/calculate-price",
        headers=regular_headers,
        json={
            "room_type_id": 1,
            "check_in": str(date.today() + timedelta(days=7)),
            "check_out": str(date.today() + timedelta(days=10)),
            "guest_loyalty_tier": 0
        }
    )
    
    # Should work with regular user token
    assert response.status_code in [200, 400]  # 400 if room_type doesn't exist


def test_pricing_rule_requires_manager_permission(client, regular_headers):
    """Test that creating pricing rules requires manager permission"""
    response = client.post(
        "/pricing-rules/",
        headers=regular_headers,
        json={
            "name": "Test Rule",
            "rule_type": "seasonal",
            "priority": 5,
            "adjustment_type": "percentage",
            "adjustment_value": 10.0,
            "is_active": True
        }
    )
    
    assert response.status_code == 403  # Forbidden for regular users
