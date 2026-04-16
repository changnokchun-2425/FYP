"""
========================================
COUPON DATA & MANAGEMENT
========================================

Purpose: Coupon system with generation, validation, and usage tracking
Usage: Import functions to handle coupon operations

Sections:
1. Coupon Types & Templates
2. Coupon Generation
3. Coupon Validation
4. Coupon Usage
5. Database Models

========================================
"""

from datetime import datetime, timedelta
import random
import string

# ==========================================================
# SECTION 1: COUPON TYPES & TEMPLATES
# Purpose: Define available coupon types and their benefits
# ==========================================================

COUPON_TYPES = {
    'WELCOME': {
        'name': '新用戶優惠券',
        'name_en': 'Welcome Coupon',
        'discount_type': 'percentage',
        'discount_value': 20,  # 20% off
        'min_purchase': 100,  # Minimum HK$100
        'max_discount': 50,  # Maximum HK$50 discount
        'valid_days': 30,
        'description': '新用戶專享20%折扣，最高減HK$50',
        'icon': '🎉'
    },
    'BIRTHDAY': {
        'name': '生日優惠券',
        'name_en': 'Birthday Coupon',
        'discount_type': 'percentage',
        'discount_value': 15,  # 15% off
        'min_purchase': 0,
        'max_discount': 100,
        'valid_days': 7,
        'description': '生日月份專享15%折扣',
        'icon': '🎂'
    },
    'FIXED50': {
        'name': 'HK$50優惠券',
        'name_en': 'HK$50 Off Coupon',
        'discount_type': 'fixed',
        'discount_value': 50,  # HK$50 off
        'min_purchase': 200,
        'max_discount': 50,
        'valid_days': 60,
        'description': '滿HK$200減HK$50',
        'icon': '💰'
    },
    'FIXED100': {
        'name': 'HK$100優惠券',
        'name_en': 'HK$100 Off Coupon',
        'discount_type': 'fixed',
        'discount_value': 100,  # HK$100 off
        'min_purchase': 500,
        'max_discount': 100,
        'valid_days': 60,
        'description': '滿HK$500減HK$100',
        'icon': '💎'
    },
    'MEMBER': {
        'name': '會員專享券',
        'name_en': 'Member Exclusive',
        'discount_type': 'percentage',
        'discount_value': 10,  # 10% off
        'min_purchase': 0,
        'max_discount': 30,
        'valid_days': 90,
        'description': '會員專享10%折扣',
        'icon': '⭐'
    },
    'WEEKEND': {
        'name': '週末特惠券',
        'name_en': 'Weekend Special',
        'discount_type': 'percentage',
        'discount_value': 25,  # 25% off
        'min_purchase': 150,
        'max_discount': 80,
        'valid_days': 14,
        'description': '週末專享25%折扣',
        'icon': '🎊'
    },
    'FREETICKET': {
        'name': '免費電影票',
        'name_en': 'Free Movie Ticket',
        'discount_type': 'fixed',
        'discount_value': 120,  # One free ticket value
        'min_purchase': 0,
        'max_discount': 120,
        'valid_days': 30,
        'description': '免費電影票一張',
        'icon': '🎟️'
    },
    # Points-based coupons (can be purchased with points)
    'POINTS_10OFF': {
        'name': '10%折扣券',
        'name_en': '10% Off Coupon',
        'discount_type': 'percentage',
        'discount_value': 10,
        'min_purchase': 100,
        'max_discount': 30,
        'valid_days': 30,
        'description': '消費滿HK$100享10%折扣',
        'icon': '🎫',
        'points_cost': 500  # Cost in points
    },
    'POINTS_20OFF': {
        'name': '20%折扣券',
        'name_en': '20% Off Coupon',
        'discount_type': 'percentage',
        'discount_value': 20,
        'min_purchase': 200,
        'max_discount': 60,
        'valid_days': 30,
        'description': '消費滿HK$200享20%折扣',
        'icon': '🎫',
        'points_cost': 1000
    },
    'POINTS_FIXED30': {
        'name': 'HK$30優惠券',
        'name_en': 'HK$30 Off Coupon',
        'discount_type': 'fixed',
        'discount_value': 30,
        'min_purchase': 150,
        'max_discount': 30,
        'valid_days': 30,
        'description': '滿HK$150減HK$30',
        'icon': '💵',
        'points_cost': 600
    },
    'POINTS_FIXED50': {
        'name': 'HK$50優惠券',
        'name_en': 'HK$50 Off Coupon',
        'discount_type': 'fixed',
        'discount_value': 50,
        'min_purchase': 250,
        'max_discount': 50,
        'valid_days': 30,
        'description': '滿HK$250減HK$50',
        'icon': '💵',
        'points_cost': 1000
    },
    'POINTS_FREETICKET': {
        'name': '免費電影票',
        'name_en': 'Free Movie Ticket',
        'discount_type': 'fixed',
        'discount_value': 100,
        'min_purchase': 0,
        'max_discount': 100,
        'valid_days': 30,
        'description': '免費電影票一張',
        'icon': '🎟️',
        'points_cost': 2000
    }
}

# ==========================================================
# SECTION 2: COUPON CODE GENERATION
# Purpose: Generate unique coupon codes
# ==========================================================

def generate_coupon_code(coupon_type, length=8):
    """
    Generate a unique coupon code
    
    Args:
        coupon_type (str): Type of coupon (e.g., 'WELCOME', 'BIRTHDAY')
        length (int): Length of random part (default 8)
    
    Returns:
        str: Unique coupon code (e.g., 'WELCOME-A3F7G9K2')
    """
    # Generate random alphanumeric string
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    # Combine type prefix with random part
    code = f"{coupon_type}-{random_part}"
    
    return code


def generate_batch_codes(coupon_type, quantity):
    """
    Generate multiple coupon codes
    
    Args:
        coupon_type (str): Type of coupon
        quantity (int): Number of codes to generate
    
    Returns:
        list: List of unique coupon codes
    """
    codes = []
    for _ in range(quantity):
        code = generate_coupon_code(coupon_type)
        codes.append(code)
    
    return codes


# ==========================================================
# SECTION 3: COUPON VALIDATION
# Purpose: Validate coupon before applying
# ==========================================================

def validate_coupon(coupon, order_total, user_id=None):
    """
    Validate if coupon can be used
    
    Args:
        coupon (Coupon): Coupon object from database
        order_total (float): Order total amount
        user_id (int): User ID attempting to use coupon
    
    Returns:
        dict: {'valid': bool, 'message': str, 'discount': float}
    """
    # Check if coupon exists
    if not coupon:
        return {
            'valid': False,
            'message': '優惠券不存在',
            'discount': 0
        }
    
    # Check if already used
    if coupon.is_used:
        return {
            'valid': False,
            'message': '此優惠券已被使用',
            'discount': 0
        }
    
    # Check expiration
    if coupon.expiry_date < datetime.now():
        return {
            'valid': False,
            'message': '此優惠券已過期',
            'discount': 0
        }
    
    # Check if user-specific coupon
    if coupon.user_id and coupon.user_id != user_id:
        return {
            'valid': False,
            'message': '此優惠券不屬於您',
            'discount': 0
        }
    
    # Get coupon template
    coupon_template = COUPON_TYPES.get(coupon.coupon_type)
    if not coupon_template:
        return {
            'valid': False,
            'message': '優惠券類型無效',
            'discount': 0
        }
    
    # Check minimum purchase requirement
    if order_total < coupon_template['min_purchase']:
        return {
            'valid': False,
            'message': f"需消費滿HK${coupon_template['min_purchase']}才可使用",
            'discount': 0
        }
    
    # Calculate discount
    discount = calculate_discount(order_total, coupon_template)
    
    return {
        'valid': True,
        'message': '優惠券有效',
        'discount': discount
    }


def calculate_discount(order_total, coupon_template):
    """
    Calculate discount amount
    
    Args:
        order_total (float): Order total amount
        coupon_template (dict): Coupon type configuration
    
    Returns:
        float: Discount amount
    """
    if coupon_template['discount_type'] == 'percentage':
        # Percentage discount
        discount = order_total * (coupon_template['discount_value'] / 100)
        # Cap at max discount
        discount = min(discount, coupon_template['max_discount'])
    else:
        # Fixed discount
        discount = coupon_template['discount_value']
    
    # Discount cannot exceed order total
    discount = min(discount, order_total)
    
    return round(discount, 2)


# ==========================================================
# SECTION 4: COUPON USAGE
# Purpose: Mark coupon as used
# ==========================================================

def use_coupon(coupon, user_id, booking_id):
    """
    Mark coupon as used
    
    Args:
        coupon (Coupon): Coupon object
        user_id (int): User who used the coupon
        booking_id (int): Associated booking ID
    
    Returns:
        bool: Success status
    """
    from app import db
    
    try:
        coupon.is_used = True
        coupon.used_date = datetime.now()
        coupon.used_by_user_id = user_id
        coupon.booking_id = booking_id
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error using coupon: {e}")
        return False


# ==========================================================
# SECTION 5: COUPON CREATION
# Purpose: Create new coupons for users
# ==========================================================

def create_coupon_for_user(user_id, coupon_type):
    """
    Create a new coupon for specific user
    
    Args:
        user_id (int): User ID to receive coupon
        coupon_type (str): Type of coupon to create
    
    Returns:
        Coupon: Created coupon object or None
    """
    from app import db
    from app.models import Coupon
    
    # Get coupon template
    template = COUPON_TYPES.get(coupon_type)
    if not template:
        return None
    
    # Generate code
    code = generate_coupon_code(coupon_type)
    
    # Calculate expiry date
    expiry_date = datetime.now() + timedelta(days=template['valid_days'])
    
    # Create coupon
    coupon = Coupon(
        code=code,
        coupon_type=coupon_type,
        user_id=user_id,
        expiry_date=expiry_date,
        is_used=False
    )
    
    try:
        db.session.add(coupon)
        db.session.commit()
        return coupon
    except Exception as e:
        db.session.rollback()
        print(f"Error creating coupon: {e}")
        return None


def create_welcome_coupon(user_id):
    """
    Create welcome coupon for new user
    
    Args:
        user_id (int): New user ID
    
    Returns:
        Coupon: Created coupon object
    """
    return create_coupon_for_user(user_id, 'WELCOME')


def create_birthday_coupon(user_id):
    """
    Create birthday coupon for user
    
    Args:
        user_id (int): User ID
    
    Returns:
        Coupon: Created coupon object
    """
    return create_coupon_for_user(user_id, 'BIRTHDAY')


# ==========================================================
# SECTION 6: COUPON QUERIES
# Purpose: Retrieve coupon information
# ==========================================================

def get_user_coupons(user_id, include_used=False):
    """
    Get all coupons for a user
    
    Args:
        user_id (int): User ID
        include_used (bool): Include used coupons
    
    Returns:
        list: List of Coupon objects
    """
    from app.models import Coupon
    
    query = Coupon.query.filter_by(user_id=user_id)
    
    if not include_used:
        query = query.filter_by(is_used=False)
        # Also filter out expired coupons
        query = query.filter(Coupon.expiry_date >= datetime.now())
    
    return query.order_by(Coupon.expiry_date.asc()).all()


def get_coupon_by_code(code):
    """
    Find coupon by code
    
    Args:
        code (str): Coupon code
    
    Returns:
        Coupon: Coupon object or None
    """
    from app.models import Coupon
    
    return Coupon.query.filter_by(code=code).first()


def get_coupon_info(coupon):
    """
    Get formatted coupon information
    
    Args:
        coupon (Coupon): Coupon object
    
    Returns:
        dict: Formatted coupon data
    """
    template = COUPON_TYPES.get(coupon.coupon_type, {})
    
    # Calculate days remaining
    days_remaining = (coupon.expiry_date - datetime.now()).days
    
    return {
        'id': coupon.id,
        'code': coupon.code,
        'type': coupon.coupon_type,
        'name': template.get('name', '優惠券'),
        'description': template.get('description', ''),
        'icon': template.get('icon', '🎫'),
        'discount_type': template.get('discount_type'),
        'discount_value': template.get('discount_value', 0),
        'min_purchase': template.get('min_purchase', 0),
        'expiry_date': coupon.expiry_date,
        'is_valid': coupon.is_valid,
        'is_used': coupon.is_used,
        'days_remaining': days_remaining
    }


# ==========================================================
# SECTION 7: POINTS EXCHANGE SYSTEM
# Purpose: Exchange points for coupons
# ==========================================================

def get_points_coupons():
    """
    Get list of coupons available for points exchange
    
    Returns:
        list: List of coupon type configurations with points cost
    """
    return {k: v for k, v in COUPON_TYPES.items() if 'points_cost' in v}


def exchange_points_for_coupon(user, coupon_type):
    """
    Exchange user points for a coupon
    
    Args:
        user (User): User object
        coupon_type (str): Type of coupon to exchange
    
    Returns:
        dict: {'success': bool, 'message': str, 'coupon': Coupon or None}
    """
    from app import db
    
    # Check if coupon type exists and is exchangeable
    if coupon_type not in COUPON_TYPES:
        return {
            'success': False,
            'message': '優惠券類型不存在',
            'coupon': None
        }
    
    coupon_template = COUPON_TYPES[coupon_type]
    
    if 'points_cost' not in coupon_template:
        return {
            'success': False,
            'message': '此優惠券不可用積分兌換',
            'coupon': None
        }
    
    points_cost = coupon_template['points_cost']
    
    # Check if user has enough points
    if user.points < points_cost:
        return {
            'success': False,
            'message': f'積分不足，需要 {points_cost} 積分，您目前有 {user.points} 積分',
            'coupon': None
        }
    
    # Deduct points
    user.points -= points_cost
    
    # Create coupon
    coupon = create_coupon_for_user(user.id, coupon_type)
    
    try:
        db.session.commit()
        return {
            'success': True,
            'message': f'成功兌換！已使用 {points_cost} 積分',
            'coupon': coupon
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'兌換失敗：{str(e)}',
            'coupon': None
        }


# ==========================================================
# USAGE EXAMPLES
# ==========================================================

"""
# In routes.py:

from app.data.coupon_system import (
    create_welcome_coupon,
    get_user_coupons,
    validate_coupon,
    use_coupon,
    get_coupon_by_code
)

# Create welcome coupon for new user
@app.route('/register', methods=['POST'])
def register():
    # ... register user ...
    user_id = new_user.id
    welcome_coupon = create_welcome_coupon(user_id)
    flash('註冊成功！已送上迎新優惠券', 'success')

# Display user's coupons
@app.route('/my-coupons')
@login_required
def my_coupons():
    coupons = get_user_coupons(current_user.id)
    return render_template('my_coupons.html.j2', coupons=coupons)

# Apply coupon to booking
@app.route('/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    code = request.form.get('coupon_code')
    total = float(request.form.get('total'))
    
    coupon = get_coupon_by_code(code)
    result = validate_coupon(coupon, total, current_user.id)
    
    if result['valid']:
        session['coupon_code'] = code
        session['discount'] = result['discount']
        flash(f'優惠券已應用！折扣HK${result["discount"]}', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('checkout'))
"""
