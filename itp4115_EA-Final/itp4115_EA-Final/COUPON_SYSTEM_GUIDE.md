# 🎫 Coupon System Documentation

## Overview
Complete coupon/discount system for FYP Cinema with validation, usage tracking, and automatic application.

## Features
- ✅ Multiple coupon types (percentage & fixed discount)
- ✅ User-specific and public coupons
- ✅ Expiration date tracking
- ✅ Single-use validation
- ✅ Automatic welcome coupons for new users
- ✅ AJAX coupon validation
- ✅ Minimum purchase requirements
- ✅ Maximum discount caps

---

## Coupon Types

### 1. WELCOME - New User Coupon 🎉
- **Discount**: 20% off
- **Min Purchase**: HK$100
- **Max Discount**: HK$50
- **Valid**: 30 days
- **Auto-created**: Yes (on registration)

### 2. BIRTHDAY - Birthday Coupon 🎂
- **Discount**: 15% off
- **Min Purchase**: None
- **Max Discount**: HK$100
- **Valid**: 7 days

### 3. FIXED50 - HK$50 Off 💰
- **Discount**: HK$50 fixed
- **Min Purchase**: HK$200
- **Valid**: 60 days

### 4. FIXED100 - HK$100 Off 💎
- **Discount**: HK$100 fixed
- **Min Purchase**: HK$500
- **Valid**: 60 days

### 5. MEMBER - Member Exclusive ⭐
- **Discount**: 10% off
- **Min Purchase**: None
- **Max Discount**: HK$30
- **Valid**: 90 days

### 6. WEEKEND - Weekend Special 🎊
- **Discount**: 25% off
- **Min Purchase**: HK$150
- **Max Discount**: HK$80
- **Valid**: 14 days

### 7. FREETICKET - Free Movie Ticket 🎟️
- **Discount**: HK$120 fixed
- **Min Purchase**: None
- **Valid**: 30 days

---

## File Structure

```
app/
├── data/
│   ├── coupon_system.py       # Coupon logic & validation
│   └── sample_movies.py        # Movie data
├── models.py                   # Coupon & Ticket database models
├── routes.py                   # Coupon routes & API endpoints
└── templates/
    ├── cinema_movie.html.j2    # Booking form with coupon input
    ├── cinema_success.html.j2  # Success page showing discount
    ├── my_coupons.html.j2      # User's coupon list
    └── my_bookings.html.j2     # Booking history with discounts

migrations/
└── versions/
    └── 7f8g9h0i1j2k_add_coupon_model.py

init_coupons.py                 # Initialize coupon database
```

---

## Database Schema

### Coupon Model
```python
class Coupon(db.Model):
    id                  # Primary key
    code                # Unique coupon code (e.g., "WELCOME-A3F7G9K2")
    coupon_type         # Type: WELCOME, BIRTHDAY, etc.
    user_id             # Owner (NULL = public coupon)
    expiry_date         # Expiration datetime
    is_used             # Usage status (True/False)
    used_date           # When it was used
    used_by_user_id     # Who used it
    booking_id          # Associated ticket
    created_date        # Creation datetime
```

### Updated Ticket Model
```python
class Ticket(db.Model):
    # ... existing fields ...
    original_price      # Price before discount
    discount_amount     # Discount applied
    coupon_code         # Coupon code used
```

---

## Usage Guide

### 1. Initialize Database

```bash
# Create coupon table
cd /workspaces/FYP/itp4115_EA-Final/itp4115_EA-Final
flask db upgrade

# Populate with sample coupons
python init_coupons.py init

# List all coupons
python init_coupons.py list

# Clear all coupons (use with caution!)
python init_coupons.py clear
```

### 2. User Flow

#### Registration (Automatic)
```python
# In routes.py - register()
user = User(username=..., email=...)
db.session.commit()

# Automatic welcome coupon
welcome_coupon = create_welcome_coupon(user.id)
# Code generated: WELCOME-A3F7G9K2
```

#### View Coupons
```
URL: /my_coupons
Shows: All user's coupons (available, used, expired)
```

#### Apply Coupon
```
1. User goes to movie booking page
2. Enters coupon code in form
3. System validates coupon
4. Discount applied to total
5. Coupon marked as used
```

### 3. Code Examples

#### Create Coupon for User
```python
from app.data.coupon_system import create_coupon_for_user

# Create birthday coupon
coupon = create_coupon_for_user(user_id=5, coupon_type='BIRTHDAY')
print(f"Code: {coupon.code}")
```

#### Validate Coupon
```python
from app.data.coupon_system import get_coupon_by_code, validate_coupon

coupon = get_coupon_by_code('WELCOME-A3F7G9K2')
result = validate_coupon(coupon, order_total=250, user_id=5)

if result['valid']:
    print(f"Discount: HK${result['discount']}")
else:
    print(f"Error: {result['message']}")
```

#### Use Coupon
```python
from app.data.coupon_system import use_coupon

# Mark as used
success = use_coupon(coupon, user_id=5, booking_id=10)
```

---

## API Endpoints

### POST /api/validate_coupon
Validate coupon code via AJAX

**Request:**
```json
{
  "coupon_code": "WELCOME-A3F7G9K2",
  "order_total": 250.00
}
```

**Response (Valid):**
```json
{
  "valid": true,
  "message": "✅ 優惠券有效！",
  "discount": 50.00,
  "new_total": 200.00,
  "coupon_name": "新用戶優惠券",
  "coupon_description": "新用戶專享20%折扣，最高減HK$50"
}
```

**Response (Invalid):**
```json
{
  "valid": false,
  "message": "❌ 此優惠券已被使用"
}
```

### GET /api/get_user_coupons
Get user's available coupons

**Response:**
```json
{
  "success": true,
  "count": 3,
  "coupons": [
    {
      "code": "WELCOME-A3F7G9K2",
      "name": "新用戶優惠券",
      "description": "新用戶專享20%折扣，最高減HK$50",
      "icon": "🎉",
      "discount_type": "percentage",
      "discount_value": 20,
      "min_purchase": 100,
      "expiry_date": "2025-12-13",
      "days_remaining": 30
    }
  ]
}
```

---

## Booking Flow with Coupon

```
1. User selects movie & showtime
2. Fills booking form (name, email, seats)
3. (Optional) Enters coupon code
4. System calculates:
   - original_price = seats × price_per_seat
   - Validates coupon
   - discount_amount = calculated discount
   - total_price = original_price - discount_amount
5. Creates Ticket with all price info
6. Marks coupon as used
7. Shows success page with price breakdown
```

---

## Template Integration

### Cinema Movie Page (Booking Form)
```html
<form method="POST" action="{{ url_for('cinema_buy_ticket') }}">
    <!-- Existing fields -->
    
    <!-- Coupon Code Input -->
    <div class="form-group">
        <label>優惠券代碼 (可選)</label>
        <input type="text" name="coupon_code" placeholder="輸入優惠券代碼">
        <button type="button" onclick="validateCoupon()">驗證</button>
    </div>
    
    <!-- Price Display -->
    <div class="price-summary">
        <p>原價: <span id="original-price">HK${{ price }}</span></p>
        <p id="discount-row" style="display:none;">
            折扣: <span id="discount-amount">HK$0</span>
        </p>
        <p>總計: <span id="total-price">HK${{ price }}</span></p>
    </div>
</form>

<script>
async function validateCoupon() {
    const code = document.querySelector('[name="coupon_code"]').value;
    const total = {{ price }};
    
    const response = await fetch('/api/validate_coupon', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({coupon_code: code, order_total: total})
    });
    
    const result = await response.json();
    
    if (result.valid) {
        // Update display
        document.getElementById('discount-row').style.display = 'block';
        document.getElementById('discount-amount').textContent = `HK$${result.discount}`;
        document.getElementById('total-price').textContent = `HK$${result.new_total}`;
        alert(result.message);
    } else {
        alert(result.message);
    }
}
</script>
```

### My Coupons Page
```html
{% for coupon in coupons %}
<div class="coupon-card {% if coupon.status != 'available' %}disabled{% endif %}">
    <div class="coupon-header">
        <span class="icon">{{ coupon.icon }}</span>
        <h3>{{ coupon.name }}</h3>
    </div>
    
    <p class="discount">{{ coupon.discount }}</p>
    <p class="code">代碼: {{ coupon.code }}</p>
    <p class="expiry">有效期至: {{ coupon.expiry }}</p>
    
    {% if coupon.status == 'available' %}
    <button onclick="copyCouponCode('{{ coupon.code }}')">複製代碼</button>
    {% elif coupon.status == 'used' %}
    <span class="badge">已使用</span>
    {% else %}
    <span class="badge">已過期</span>
    {% endif %}
</div>
{% endfor %}
```

---

## Validation Rules

### Coupon Validation Checks:
1. ✅ Coupon exists in database
2. ✅ Not already used (`is_used = False`)
3. ✅ Not expired (`expiry_date > now`)
4. ✅ Belongs to user (if user-specific)
5. ✅ Meets minimum purchase requirement
6. ✅ Order total > 0

### Discount Calculation:
```python
# Percentage discount
if discount_type == 'percentage':
    discount = order_total × (discount_value / 100)
    discount = min(discount, max_discount)  # Cap at maximum

# Fixed discount
else:
    discount = discount_value

# Final check
discount = min(discount, order_total)  # Can't exceed total
```

---

## Testing

### Manual Test Cases

1. **New User Registration**
   - Register → Check `/my_coupons` → Should see WELCOME coupon

2. **Valid Coupon Application**
   - Book ticket (HK$200) → Enter valid coupon → See discount applied

3. **Invalid Coupon Tests**
   - Used coupon → "已被使用"
   - Expired coupon → "已過期"
   - Wrong owner → "不屬於您"
   - Below min purchase → "需消費滿HK$X"

4. **Booking with Coupon**
   - Complete booking → Check `my_bookings` → See original price & discount
   - Check `my_coupons` → Coupon status = "已使用"

---

## Troubleshooting

### Coupon not appearing?
```python
# Check if coupon created
from app.models import Coupon
coupons = Coupon.query.filter_by(user_id=USER_ID).all()
print(coupons)
```

### Validation failing?
```python
# Debug validation
result = validate_coupon(coupon, order_total, user_id)
print(f"Valid: {result['valid']}")
print(f"Message: {result['message']}")
```

### Database not updated?
```bash
# Run migration
flask db upgrade

# Check tables
flask shell
>>> from app.models import Coupon
>>> Coupon.query.count()
```

---

## Future Enhancements

1. **Admin Panel**
   - Create/edit/delete coupons via web interface
   - View usage statistics
   - Bulk coupon generation

2. **Advanced Features**
   - Time-based coupons (weekday/weekend only)
   - Movie-specific coupons
   - Multi-use coupons with usage limits
   - Referral coupons

3. **Marketing**
   - Email coupon delivery
   - Birthday auto-coupons
   - Loyalty program integration
   - Seasonal campaigns

---

## Support

For issues or questions:
1. Check this documentation
2. Review `coupon_system.py` code comments
3. Test with `init_coupons.py list` command
4. Check Flask logs for errors

**Last Updated**: 2025-11-13
