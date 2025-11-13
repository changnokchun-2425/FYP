"""
========================================
INITIALIZE COUPON SYSTEM
========================================

Purpose: Create sample coupons for testing and demo
Usage: Run this script to populate database with coupons

Run with: python init_coupons.py

========================================
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from app.models import User, Coupon
from app.data.coupon_system import create_coupon_for_user, generate_coupon_code, COUPON_TYPES
from datetime import datetime, timedelta

def init_coupons():
    """Initialize coupon system with sample data"""
    
    with app.app_context():
        print("🎫 Initializing Coupon System...")
        print("=" * 50)
        
        # Get all users
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database!")
            print("   Please create users first before initializing coupons.")
            return
        
        print(f"✅ Found {len(users)} users")
        print()
        
        # Create welcome coupons for all existing users who don't have one
        print("📝 Creating welcome coupons...")
        welcome_count = 0
        for user in users:
            # Check if user already has a welcome coupon
            existing = Coupon.query.filter_by(
                user_id=user.id,
                coupon_type='WELCOME'
            ).first()
            
            if not existing:
                coupon = create_coupon_for_user(user.id, 'WELCOME')
                if coupon:
                    print(f"   ✅ Created WELCOME coupon for {user.username}: {coupon.code}")
                    welcome_count += 1
        
        print(f"✅ Created {welcome_count} welcome coupons")
        print()
        
        # Create some public coupons (not user-specific)
        print("📝 Creating public coupons...")
        public_coupons = [
            ('FIXED50', 5),   # 5x HK$50 off coupons
            ('FIXED100', 3),  # 3x HK$100 off coupons
            ('WEEKEND', 10),  # 10x Weekend special coupons
            ('MEMBER', 15),   # 15x Member exclusive coupons
        ]
        
        public_count = 0
        for coupon_type, quantity in public_coupons:
            template = COUPON_TYPES.get(coupon_type)
            if not template:
                continue
            
            for i in range(quantity):
                # Check if code already exists
                code = generate_coupon_code(coupon_type)
                while Coupon.query.filter_by(code=code).first():
                    code = generate_coupon_code(coupon_type)
                
                # Create public coupon (no user_id)
                expiry_date = datetime.now() + timedelta(days=template['valid_days'])
                
                coupon = Coupon(
                    code=code,
                    coupon_type=coupon_type,
                    user_id=None,  # Public coupon
                    expiry_date=expiry_date,
                    is_used=False
                )
                
                db.session.add(coupon)
                public_count += 1
            
            print(f"   ✅ Created {quantity}x {coupon_type} coupons")
        
        try:
            db.session.commit()
            print(f"✅ Created {public_count} public coupons")
            print()
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating public coupons: {e}")
            return
        
        # Display summary
        print("=" * 50)
        print("📊 COUPON SUMMARY")
        print("=" * 50)
        
        for coupon_type, template in COUPON_TYPES.items():
            count = Coupon.query.filter_by(coupon_type=coupon_type, is_used=False).count()
            if count > 0:
                print(f"{template['icon']} {template['name']}: {count} coupons")
        
        print()
        total_coupons = Coupon.query.count()
        available_coupons = Coupon.query.filter_by(is_used=False).count()
        print(f"Total Coupons: {total_coupons}")
        print(f"Available: {available_coupons}")
        print(f"Used: {total_coupons - available_coupons}")
        print()
        print("✅ Coupon system initialized successfully!")


def list_all_coupons():
    """List all coupons in the database"""
    
    with app.app_context():
        print("🎫 ALL COUPONS IN DATABASE")
        print("=" * 80)
        
        coupons = Coupon.query.all()
        
        if not coupons:
            print("No coupons found in database.")
            return
        
        print(f"{'Code':<25} {'Type':<15} {'Owner':<15} {'Status':<10} {'Expiry'}")
        print("-" * 80)
        
        for coupon in coupons:
            owner = coupon.owner.username if coupon.owner else 'PUBLIC'
            status = 'USED' if coupon.is_used else ('EXPIRED' if coupon.is_expired else 'VALID')
            expiry = coupon.expiry_date.strftime('%Y-%m-%d')
            
            print(f"{coupon.code:<25} {coupon.coupon_type:<15} {owner:<15} {status:<10} {expiry}")
        
        print("-" * 80)
        print(f"Total: {len(coupons)} coupons")


def clear_all_coupons():
    """Clear all coupons from database (use with caution!)"""
    
    with app.app_context():
        confirm = input("⚠️  Are you sure you want to delete ALL coupons? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        
        try:
            count = Coupon.query.delete()
            db.session.commit()
            print(f"✅ Deleted {count} coupons from database.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Coupon System Management')
    parser.add_argument('action', choices=['init', 'list', 'clear'], 
                       help='Action to perform: init (create coupons), list (show all), clear (delete all)')
    
    args = parser.parse_args()
    
    if args.action == 'init':
        init_coupons()
    elif args.action == 'list':
        list_all_coupons()
    elif args.action == 'clear':
        clear_all_coupons()
