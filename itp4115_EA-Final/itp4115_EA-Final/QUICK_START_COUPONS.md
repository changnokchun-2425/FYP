# 🚀 Quick Start: Coupon System

## ✅ System is Now Active!

The coupon system has been successfully initialized with **44 coupons**:
- 11 welcome coupons (one for each existing user)
- 5 HK$50 off coupons
- 3 HK$100 off coupons  
- 10 weekend special coupons
- 15 member exclusive coupons

---

## 🎯 How to Use Coupons (For Users)

### Method 1: View Your Coupons
1. **Login** to your account
2. Go to: **`http://localhost:5000/my_coupons`**
3. You'll see all your available coupons with codes

### Method 2: Use Coupon When Booking
1. Go to **Cinema** → Select a **Movie**
2. Click **"Buy Ticket"**
3. Fill in the booking form
4. **Enter coupon code** in the "優惠券代碼" field
5. Click **Submit** → Discount will be applied automatically!

### Example Coupon Codes You Can Use:

**Welcome Coupons** (20% off, max HK$50):
- `WELCOME-Y8DGBAW6` (for user: 111)
- `WELCOME-FHBF7OPM` (for user: 1)
- `WELCOME-TIY3G7D0` (for user: test)
- `WELCOME-17UV63HX` (for user: admin)

**Public Coupons** (Anyone can use):
- `FIXED50-CF6X2W27` (HK$50 off, min purchase HK$200)
- `FIXED100-...` (HK$100 off, min purchase HK$500)
- `WEEKEND-...` (25% off, min purchase HK$150)
- `MEMBER-...` (10% off, no minimum)

---

## 🔧 Testing the System

### Test Scenario 1: Apply Welcome Coupon
```
1. Login as user "111"
2. Book 3 tickets (3 × HK$100 = HK$300)
3. Enter coupon: WELCOME-Y8DGBAW6
4. Result: 20% discount = HK$50 off → Pay HK$250
```

### Test Scenario 2: Public Coupon
```
1. Login as any user
2. Book 2 tickets (2 × HK$100 = HK$200)
3. Enter coupon: FIXED50-CF6X2W27
4. Result: HK$50 off → Pay HK$150
```

### Test Scenario 3: New User Registration
```
1. Register a NEW account
2. Automatic welcome coupon created!
3. Go to /my_coupons to see it
```

---

## 📱 Where to Access

### User Pages:
- **My Coupons**: `http://localhost:5000/my_coupons`
- **My Bookings**: `http://localhost:5000/my_bookings` (see discounts applied)
- **Cinema Index**: `http://localhost:5000/cinema` (browse movies)
- **Profile**: `http://localhost:5000/profile`

### Admin Commands:
```bash
# List all coupons
python init_coupons.py list

# Clear all coupons (careful!)
python init_coupons.py clear

# Re-initialize
python init_coupons.py init
```

---

## 🎬 Complete Booking Flow with Coupon

**Step-by-step:**
1. **Login** → Choose username (e.g., "111", "test", "admin")
2. **Go to Cinema** → Click "現正熱映" or visit `/cinema`
3. **Select Movie** → Click "立即購票" on any movie
4. **Fill Form**:
   - Showtime: Select any time
   - Name: Your name
   - Email: Your email
   - Seats: Number of tickets (e.g., 2)
   - **Coupon Code**: Enter your code (e.g., `WELCOME-Y8DGBAW6`)
5. **Submit** → See success page with:
   - Original Price: HK$200
   - Discount: -HK$40 (or whatever applies)
   - **Total: HK$160**
6. **Check History** → Go to `/my_bookings` to see the transaction
7. **Check Coupons** → Go to `/my_coupons` to see coupon is now "已使用" (used)

---

## 🛠️ Troubleshooting

### "Coupon invalid" error?
- Check if coupon belongs to you (welcome coupons are user-specific)
- Check if already used (each coupon is single-use)
- Check minimum purchase requirement
- Verify coupon code is correct (case-sensitive)

### Can't see coupons at /my_coupons?
- Make sure you're logged in
- Run: `python init_coupons.py list` to see all coupons
- Welcome coupons are tied to specific users

### Want to test with fresh coupons?
```bash
python init_coupons.py clear  # Delete all
python init_coupons.py init   # Create new ones
```

---

## 📊 Coupon Rules Reference

| Type | Discount | Min Purchase | Max Discount | Valid Days |
|------|----------|--------------|--------------|------------|
| WELCOME | 20% | HK$100 | HK$50 | 30 |
| BIRTHDAY | 15% | None | HK$100 | 7 |
| FIXED50 | HK$50 | HK$200 | HK$50 | 60 |
| FIXED100 | HK$100 | HK$500 | HK$100 | 60 |
| MEMBER | 10% | None | HK$30 | 90 |
| WEEKEND | 25% | HK$150 | HK$80 | 14 |
| FREETICKET | HK$120 | None | HK$120 | 30 |

---

## ✨ What Happens Automatically

1. **New User Registers** → Gets welcome coupon automatically
2. **Coupon Applied** → Marked as "used" after booking
3. **Expired Coupons** → System won't allow use after expiry date
4. **Booking Record** → Stores original price + discount + final price

---

## 🎉 You're Ready!

**Start the server:**
```bash
cd /workspaces/FYP/itp4115_EA-Final/itp4115_EA-Final
flask --app run.py run
```

**Then visit:**
- Login page: `http://localhost:5000/login`
- Your coupons: `http://localhost:5000/my_coupons` (after login)
- Cinema: `http://localhost:5000/cinema`

**Happy testing!** 🎫🎬
