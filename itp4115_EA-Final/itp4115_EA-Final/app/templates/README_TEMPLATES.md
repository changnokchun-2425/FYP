# 📁 Templates Directory - Code Structure Guide

## 🎯 Overview
This directory contains all HTML templates (Jinja2) for the FYP Cinema application.
Each template is well-organized with clear sections and comments for easy maintenance.

---

## 📋 Template Structure Convention

All templates follow this consistent structure:

```jinja
{# ========================================
   TEMPLATE NAME
   ========================================
   Purpose: Brief description
   Features:
   - Feature 1
   - Feature 2
======================================== #}

<!DOCTYPE html>
<html>
<head>
    <!-- ========== META TAGS ========== -->
    <!-- ========== EXTERNAL STYLESHEETS ========== -->
    <!-- ========== PAGE STYLES ========== -->
    <style>
        /* ========== SECTION NAME ========== */
    </style>
</head>
<body>
    <!-- ========================================
         SECTION NAME
    ======================================== -->
    
    <!-- ========================================
         JAVASCRIPT
    ======================================== -->
    <script>
        /* ========== FUNCTION GROUP ========== */
    </script>
</body>
</html>
```

---

## 🗂️ Template Files

### 🏠 Core Templates

#### `base.html.j2` - Master Template
- **Purpose**: Base template extended by other pages
- **Features**:
  - Common header with cinema branding
  - Navigation bar (dynamic based on authentication)
  - Flash message display
  - Common footer
  - Bootstrap integration
- **Usage**: `{% extends "base.html.j2" %}` then `{% block content %}...{% endblock %}`

#### `index.html.j2` - Homepage
- **Purpose**: Main landing page
- **Features**:
  - Animated hero section
  - Featured movies grid
  - Call-to-action buttons
  - Particle effects
- **Extends**: `base.html.j2`

---

### 🎬 Cinema Pages

#### `cinema_index.html.j2` - Now Showing
- **Purpose**: Display currently showing movies
- **Features**:
  - Movie grid layout
  - Movie cards with posters
  - Quick booking buttons
- **Sections**:
  - Header
  - Navigation
  - Movie Grid (loops through `movies`)
  - Footer

#### `cinema_movie.html.j2` - Movie Detail
- **Purpose**: Individual movie information and booking
- **Features**:
  - Movie poster and details
  - Showtime selection
  - Booking form
  - Price calculator
  - Login gate for bookings
- **JavaScript**: `updatePrice()` - calculates total based on seats
- **Variables**: `movie`, `current_user`

#### `cinema_coming_soon.html.j2` - Upcoming Movies
- **Purpose**: Display upcoming releases
- **Features**:
  - Release date badges
  - Notify me buttons
  - Timeline view
- **Variables**: `movies` (coming soon list)

#### `cinema_success.html.j2` - Booking Confirmation
- **Purpose**: Confirm successful ticket purchase
- **Features**:
  - Booking details summary
  - QR code placeholder
  - Important instructions
  - Action buttons
- **Variables**: `ticket` (booking object)

---

### 👤 User Account Pages

#### `login.html.j2` - User Login
- **Purpose**: User authentication
- **Features**:
  - Username/Password input
  - Remember me checkbox
  - Math captcha validation
  - Flash messages
- **JavaScript**:
  - `generateCaptcha()` - creates math problem
  - `validateCaptcha()` - checks answer
- **Form**: `LoginForm`

#### `register.html.j2` - User Registration
- **Purpose**: New account creation
- **Features**:
  - Username, email, password fields
  - Password confirmation
  - Form validation
- **Form**: `RegistrationForm`

#### `profile.html.j2` - User Profile
- **Purpose**: Display user account information
- **Features**:
  - Account information cards
  - Membership status
  - Recent activity stats
  - Quick action buttons
  - Admin-specific features
- **Sections**:
  - Profile Header (avatar & username)
  - Info Grid (3 cards)
  - Quick Actions
- **Variables**: `user`

#### `edit_profile.html.j2` - Edit Profile
- **Purpose**: Update account information
- **Features**:
  - Update username, email, phone
  - Change password with validation
  - Avatar upload placeholder
  - Delete account option
- **JavaScript**:
  - `togglePassword()` - show/hide password
  - Form validation on submit
- **Sections**:
  - Basic Information
  - Password Change
  - Danger Zone (delete account)

---

### 🎟️ Booking & Activity Pages

#### `my_bookings.html.j2` - Booking History
- **Purpose**: Display ticket booking history
- **Features**:
  - List all bookings
  - Status badges (confirmed/cancelled)
  - Booking details
  - Cancel ticket functionality
  - Empty state handling
- **Variables**: `bookings` (list of Ticket objects)
- **JavaScript**: Tab switching

#### `my_movies.html.j2` - Browse Movies
- **Purpose**: Movie browsing and discovery
- **Features**:
  - Movie grid
  - Genre filters
  - Viewing statistics
  - Quick booking
- **Variables**: `movies`
- **JavaScript**: Filter button functionality

#### `my_coupons.html.j2` - My Coupons
- **Purpose**: Display and manage coupons
- **Features**:
  - Coupon cards with codes
  - Copy to clipboard
  - Expiry date tracking
  - Status indicators
  - Statistics banner
- **Variables**: `coupons`
- **JavaScript**:
  - Tab switching
  - `copyCode()` - clipboard copy

---

## 🎨 Design System

### Color Palette
```css
/* Primary Colors */
--dark-bg: #0a0a0a to #1a1a1a (gradient)
--header-gradient: #1e3c72 to #2a5298
--accent-red: #e50914
--card-bg: #2a2a2a to #1a1a1a

/* Text Colors */
--text-primary: #fff
--text-secondary: #ccc
--text-muted: #888

/* UI Elements */
--border: #333, #444
--nav-bg: #1a1a1a
--footer-border: #2a5298
```

### Component Patterns

#### Navigation Bar
```html
<nav class="cinema-nav">
    <a href="...">🎬 現正熱映</a>
    <a href="...">📅 即將上映</a>
    {% if current_user.is_authenticated %}
        <a href="...">👤 個人中心</a>
        <a href="...">🚪 登出</a>
    {% else %}
        <a href="...">🔑 登入</a>
        <a href="...">✨ 註冊</a>
    {% endif %}
</nav>
```

#### Flash Messages
```jinja
{% with messages = get_flashed_messages() %}
    {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
                <div class="alert">{{ message }}</div>
            {% endfor %}
        </div>
    {% endif %}
{% endwith %}
```

#### Movie Card
```html
<div class="movie-card">
    <img src="{{ movie.poster }}" alt="{{ movie.title }}">
    <div class="movie-info">
        <h3>{{ movie.title }}</h3>
        <p>{{ movie.description }}</p>
        <a href="..." class="btn">購票</a>
    </div>
</div>
```

---

## 🔧 Template Variables Reference

### Common Variables
- `current_user` - Logged in user object (Flask-Login)
- `url_for()` - Generate URLs for routes

### Page-Specific Variables

| Template | Variable | Type | Description |
|----------|----------|------|-------------|
| cinema_index | `movies` | List | Currently showing movies |
| cinema_movie | `movie` | Object | Single movie details |
| cinema_coming_soon | `movies` | List | Upcoming movies |
| cinema_success | `ticket` | Object | Booking confirmation |
| my_bookings | `bookings` | List | User's ticket bookings |
| my_coupons | `coupons` | List | User's coupons |
| profile | `user` | Object | User account data |

---

## 📝 Code Style Guidelines

### Jinja2 Comments
```jinja
{# Single line comment #}

{# ========================================
   Multi-line section header
======================================== #}
```

### HTML Comments
```html
<!-- ========================================
     SECTION NAME
======================================== -->

<!-- Single line comment -->
```

### CSS Comments
```css
/* ========== SECTION NAME ========== */

/* Single comment */
```

### JavaScript Comments
```javascript
/* ========== FUNCTION GROUP ========== */

// Single line comment

/**
 * Multi-line function documentation
 */
```

---

## 🚀 Best Practices

### 1. **Consistent Indentation**
- Use 4 spaces for indentation
- Keep HTML hierarchy clear

### 2. **Section Organization**
```
1. File header comment
2. DOCTYPE and HTML tag
3. HEAD section
   - Meta tags
   - External stylesheets
   - Page styles
4. BODY section
   - Header
   - Navigation
   - Main content
   - Footer
   - JavaScript
```

### 3. **Comment Placement**
- Place comments BEFORE the section they describe
- Use divider comments for major sections
- Add inline comments for complex logic

### 4. **Variable Naming**
- Use descriptive names: `movie`, `bookings`, not `m`, `b`
- Follow Python naming conventions in Jinja2

### 5. **Form Handling**
```jinja
<form method="POST">
    {{ form.hidden_tag() }}  {# CSRF protection #}
    
    <!-- Field with error handling -->
    {{ form.username.label }}
    {{ form.username(size=32) }}
    {% for error in form.username.errors %}
        <span class="error">{{ error }}</span>
    {% endfor %}
</form>
```

---

## 🔍 Debugging Tips

### Check Template Rendering
```python
# In routes.py
return render_template('template.html.j2', 
                      variable1=value1,
                      variable2=value2)
```

### Common Issues
1. **Variable not found**: Check if passed from route
2. **Template not rendering**: Check file path and extension
3. **CSS not loading**: Clear browser cache, check static file path

---

## 📚 Resources

- **Jinja2 Documentation**: https://jinja.palletsprojects.com/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Bootstrap 4 Docs**: https://getbootstrap.com/docs/4.3/

---

## ✅ Maintenance Checklist

When editing templates:
- [ ] Add/update file header comment
- [ ] Use section divider comments
- [ ] Comment complex logic
- [ ] Test on mobile (responsive design)
- [ ] Check flash messages display
- [ ] Verify form CSRF protection
- [ ] Test all links and buttons
- [ ] Check error handling

---

**Last Updated**: 2025-11-13
**Maintained By**: FYP Cinema Development Team
