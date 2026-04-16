from flask import render_template, redirect, flash, url_for, request, jsonify, make_response
from flask_login import login_required, current_user, login_user, logout_user 
from urllib.parse import urlparse
from flask.cli import AppGroup
from datetime import datetime, timedelta
import sqlite3
import os

from app import app, db
from app.forms import LoginForm, RegistrationForm, ProductForm, CategoryForm
from app.models import (
    User,
    Category,
    Product,
    Article,
    Comment,
    Tag,
    ArticleTag,
    Source,
    Reaction,
    Author,
    Newsletter,
    Ticket,
    Coupon,
    Movie,
    Cinema,
    Hall,
    Showtime,
)
from app.data.coupon_system import (
    create_welcome_coupon,
    get_user_coupons,
    validate_coupon,
    use_coupon,
    get_coupon_by_code,
    get_coupon_info,
    COUPON_TYPES,
    get_points_coupons,
    exchange_points_for_coupon
)
from app.data import sample_movies
admin_cli = AppGroup('admin')


def _parse_duration_to_minutes(raw_duration):
    """Convert strings like '127 分鐘' or '181分鐘' to integer minutes."""
    if raw_duration is None:
        return None
    import re
    match = re.search(r"(\d+)", str(raw_duration))
    return int(match.group(1)) if match else None


def _format_duration_label(minutes):
    if minutes is None:
        return "未知時長"
    return f"{minutes} 分鐘"


def _format_showtime_label(showtime_obj):
    dt = datetime.combine(showtime_obj.show_date, showtime_obj.show_time)
    return dt.strftime("%Y-%m-%d %H:%M")


def _parse_seat_numbers(raw_seat_numbers):
    if not raw_seat_numbers:
        return []
    return [seat.strip().upper() for seat in str(raw_seat_numbers).split(',') if seat.strip()]


def _get_sold_seats_for_showtime(showtime_obj):
    sold = set()
    showtime_label = _format_showtime_label(showtime_obj)
    tickets = Ticket.query.filter_by(movie_id=showtime_obj.movie_id, showtime=showtime_label).all()
    for ticket in tickets:
        if ticket.status == 'cancelled':
            continue
        sold.update(_parse_seat_numbers(ticket.seat_numbers))
    return sold


def _movie_view_model(movie, include_showtimes=False):
    showtimes = []
    if include_showtimes:
        showtimes = [
            {
                'id': st.id,
                'label': _format_showtime_label(st),
                'price': st.price,
            }
            for st in sorted(movie.showtimes, key=lambda s: (s.show_date, s.show_time))
        ]

    # Use first showtime price as display price
    display_price = showtimes[0]['price'] if showtimes else 120

    return {
        'id': movie.id,
        'title': movie.title,
        'description': movie.description,
        'genre': movie.genre,
        'rating': movie.rating,
        'duration': _format_duration_label(movie.duration),
        'poster': movie.poster_url,
        'price': display_price,
        'release_date': movie.release_date.strftime('%Y-%m') if movie.release_date else '待公布',
        'showtimes': showtimes,
    }


def seed_cinema_content():
    """Seed movies, cinema, hall, and showtimes into the database if empty."""
    if Movie.query.count() > 0:
        return

    # Create a default cinema and hall
    cinema = Cinema.query.first()
    if cinema is None:
        cinema = Cinema(
            name='FYP Cinema - Central',
            location='Central',
            district='Central',
            address='123 Queen\'s Road Central, Hong Kong',
            phone='2317 6666',
            email='support@fypcinema.test',
            facilities='{"imax": true, "mx4d": true, "parking": true}'
        )
        db.session.add(cinema)
        db.session.flush()

    hall = Hall.query.first()
    if hall is None:
        hall = Hall(
            cinema_id=cinema.id,
            name='Hall 1',
            hall_type='standard',
            total_seats=120,
            rows=10,
            columns=12,
            is_active=True,
        )
        db.session.add(hall)
        db.session.flush()

    def _create_movie_entries(raw_movies, status):
        for entry in raw_movies:
            duration_minutes = _parse_duration_to_minutes(entry.get('duration'))
            release_date = None
            if entry.get('release_date'):
                try:
                    release_date = datetime.strptime(entry['release_date'], '%Y-%m-%d').date()
                except ValueError:
                    try:
                        release_date = datetime.strptime(entry['release_date'], '%Y-%m').date()
                    except ValueError:
                        release_date = None

            movie = Movie(
                title=entry.get('title'),
                title_en=entry.get('title_en'),
                description=entry.get('description'),
                genre=entry.get('genre'),
                duration=duration_minutes,
                release_date=release_date,
                rating=entry.get('rating'),
                director=entry.get('director'),
                cast=entry.get('cast'),
                poster_url=entry.get('poster'),
                trailer_url=entry.get('trailer_url'),
                language=entry.get('language'),
                status=status,
            )
            db.session.add(movie)
            db.session.flush()

            base_price = entry.get('price', 120)
            # Create a few showtimes over the next 3 days
            time_slots = [10, 14, 18, 21]
            for day_offset in range(0, 3):
                for hour in time_slots:
                    st = Showtime(
                        movie_id=movie.id,
                        hall_id=hall.id,
                        show_date=datetime.utcnow().date() + timedelta(days=day_offset),
                        show_time=datetime.min.time().replace(hour=hour, minute=0),
                        price=base_price,
                        available_seats=hall.total_seats,
                        status='available',
                    )
                    db.session.add(st)

    _create_movie_entries(sample_movies.NOW_SHOWING_MOVIES, 'now_showing')
    _create_movie_entries(sample_movies.COMING_SOON_MOVIES, 'coming_soon')

    db.session.commit()


def ensure_default_admin():
    """Create a default admin account when none exists."""
    existing_admin = User.query.filter_by(is_admin=True).first()
    if existing_admin:
        print(f"[Admin Init] Admin already present: {existing_admin.username}")
        return

    username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
    email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
    password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')

    # Avoid collision with a non-admin user who might already have this username
    collision = User.query.filter_by(username=username).first()
    if collision:
        username = f"{username}_admin"
        email = f"{username}@example.com"

    admin = User(username=username, email=email, is_admin=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"[Admin Init] Created default admin '{username}' with password '{password}'")

# Initialize database - add seat_numbers column if it doesn't exist
def init_seat_numbers_column():
    """Add seat_numbers column to ticket table if it doesn't exist"""
    try:
        # Get the correct database path
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(basedir, 'app.db')
        
        print(f"[DB Init] Checking database at: {db_path}")
        print(f"[DB Init] Database exists: {os.path.exists(db_path)}")
        
        if not os.path.exists(db_path):
            print("[DB Init] Database file not found, skipping column check")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if ticket table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ticket'")
        if not cursor.fetchone():
            print("[DB Init] Ticket table doesn't exist yet, skipping column check")
            conn.close()
            return
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(ticket)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"[DB Init] Current ticket columns: {columns}")
        
        if 'seat_numbers' not in columns:
            print("[DB Init] Adding seat_numbers column...")
            cursor.execute("ALTER TABLE ticket ADD COLUMN seat_numbers VARCHAR(256)")
            conn.commit()
            print("[DB Init] ✓ Successfully added seat_numbers column to ticket table")
        else:
            print("[DB Init] ✓ seat_numbers column already exists")
        
        conn.close()
    except Exception as e:
        print(f"[DB Init] Error: {e}")
        import traceback
        traceback.print_exc()

# Run initialization
try:
    with app.app_context():
        init_seat_numbers_column()
        seed_cinema_content()
        ensure_default_admin()
except Exception as e:
    print(f"[DB Init] Failed to initialize: {e}")


@app.cli.command('init-db')
def init_db_command():
    """Initialize database with seat_numbers column"""
    print("Initializing database...")
    init_seat_numbers_column()
    print("Database initialization complete!")


@app.route("/")
def home():
    return redirect(url_for('cinema_index'))

@app.route("/index")
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template("index.html.j2", title="Home", posts=posts)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for('index')
        return redirect(next_page)  # Added return here

    return render_template('login.html.j2', title="Sign In", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

####################################################################################################

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Create welcome coupon for new user
        try:
            welcome_coupon = create_welcome_coupon(user.id)
            if welcome_coupon:
                flash(f'恭喜註冊成功！已送上迎新優惠券：{welcome_coupon.code}', 'success')
            else:
                flash('Congraduations, you are now a registered user!')
        except:
            flash('Congraduations, you are now a registered user!')
        
        return redirect(url_for('login'))
    return render_template('register.html.j2', title="Register", form=form)

####################################################################################################

@app.route("/sales")
def sales():
    sales_items = [
        {
            'item': 'Laptop',
            'price': '$999',
            'description': 'High-performance laptop for all your needs.'
        },
        {
            'item': 'Smartphone',
            'price': '$699',
            'description': 'Latest model with advanced features.'
        },
        {
            'item': 'Headphones',
            'price': '$199',
            'description': 'Noise-cancelling headphones for immersive sound.'
        }
    ]

    return render_template("sales.html.j2", title="Sales", sales_items=sales_items)
####################################################################################################
@app.route("/profile")
@login_required
def profile():
    user = current_user  # Get the currently logged-in user
    
    # Get available coupons count
    available_coupons = get_user_coupons(user.id, include_used=False)
    coupon_count = len(available_coupons)
    
    # Initialize points if None
    if user.points is None:
        user.points = 0
        db.session.commit()
    
    # Get user's ticket statistics
    user_tickets = Ticket.query.filter_by(user_id=user.id).order_by(Ticket.booking_date.desc()).all()
    total_bookings = len(user_tickets)
    
    # Calculate last booking time
    last_booking_days = None
    last_booking_date = None
    if user_tickets:
        last_ticket = user_tickets[0]
        last_booking_date = last_ticket.booking_date
        time_diff = datetime.utcnow() - last_booking_date
        last_booking_days = time_diff.days
    
    # Calculate favorite genre from bookings
    from collections import Counter
    genre_counter = Counter()
    for ticket in user_tickets:
        # Fetch movie genre from DB for each booking
        movie_obj = Movie.query.get(ticket.movie_id)
        if movie_obj and movie_obj.genre:
            genre_counter[movie_obj.genre] += 1
    
    favorite_genre = genre_counter.most_common(1)[0][0] if genre_counter else "尚未觀影"
    
    return render_template("profile.html.j2", 
                         title="Profile", 
                         user=user, 
                         coupon_count=coupon_count,
                         total_bookings=total_bookings,
                         last_booking_days=last_booking_days,
                         favorite_genre=favorite_genre)

####################################################################################################

@app.route('/news')
def news():
    # Fetch all articles, including related authors, categories, and tags
    articles = Article.query.all()

    # Ensure that necessary relationships are loaded
    for article in articles:
        article.author  # Load author
        article.category  # Load category
        article.article_tags  # Load article tags
        article.reactions  # Load reactions if needed
        # Note: You might want to use joined loading or lazy loading based on your needs

    # Fetch sources if you want to display them separately or alongside articles
    sources = Source.query.all()

    return render_template('news.html.j2', articles=articles, sources=sources)

@app.route('/subscribe', methods=['POST'])
def subscribe_newsletter():
    email = request.form['email']
    # Logic to add the email to newsletter subscriptions
    # For example:
    new_subscription = Newsletter(email=email)
    db.session.add(new_subscription)
    db.session.commit()
    return redirect(url_for('news'))  # Redirect back to the news page

@app.route('/add_comment/<int:article_id>', methods=['POST'])
def add_comment(article_id):
    content = request.form['content']
    user_id = 1  # Replace with actual user ID from session or context
    new_comment = Comment(content=content, article_id=article_id, user_id=user_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('news'))

@app.route('/add_reaction/<int:article_id>', methods=['POST'])
def add_reaction(article_id):
    reaction_type = request.form['reaction_type']
    user_id = 1  # Replace with actual user ID from session or context
    new_reaction = Reaction(article_id=article_id, user_id=user_id, reaction_type=reaction_type)
    db.session.add(new_reaction)
    db.session.commit()
    return redirect(url_for('news'))

@app.route('/set_theme/<theme>')
def set_theme(theme):
    response = make_response(redirect(url_for('news')))
    response.set_cookie('theme', theme)  # Set a cookie for the theme
    return response
####################################################################################################

@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('admin_login'))

        # Check if the user is an admin
        if not user.is_admin:
            flash('You do not have admin access!')
            return redirect(url_for('admin_login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for('admin_console')
        return redirect(next_page)

    return render_template('login.html.j2', title="Admin Sign In", form=form)

@app.route("/admin")
@login_required
def admin_console():
    if not current_user.is_admin:
        flash('You do not have admin access!')
        return redirect(url_for('index'))

    stats = {
        'products': Product.query.count(),
        'categories': Category.query.count(),
        'tickets': Ticket.query.count(),
        'movies': Movie.query.count(),
    }

    return render_template(
        'admin_console.html.j2',
        title="Admin Console",
        stats=stats,
        now_showing_total=Movie.query.filter_by(status='now_showing').count(),
        coming_soon_total=Movie.query.filter_by(status='coming_soon').count()
    )


@app.route('/admin/tickets')
@login_required
def admin_tickets():
    if not current_user.is_admin:
        flash('You do not have admin access!')
        return redirect(url_for('index'))

    movie_id = request.args.get('movie_id', type=int)
    buyer_query = (request.args.get('buyer') or '').strip()
    booked_date_raw = (request.args.get('booked_at') or '').strip()
    tickets_query = Ticket.query
    if movie_id:
        tickets_query = tickets_query.filter_by(movie_id=movie_id)

    if buyer_query:
        buyer_like = f"%{buyer_query}%"
        tickets_query = tickets_query.filter(
            (Ticket.customer_name.ilike(buyer_like)) |
            (Ticket.customer_email.ilike(buyer_like))
        )

    if booked_date_raw:
        try:
            booked_date = datetime.strptime(booked_date_raw, '%Y-%m-%d')
            start = booked_date
            end = booked_date + timedelta(days=1)
            tickets_query = tickets_query.filter(Ticket.booking_date >= start, Ticket.booking_date < end)
        except ValueError:
            flash('Invalid date format for Booked At. Use YYYY-MM-DD.', 'error')

    tickets = tickets_query.order_by(Ticket.booking_date.desc()).all()
    movie_rows = Movie.query.order_by(Movie.title.asc()).all()
    movie_options = [{'id': movie.id, 'title': movie.title} for movie in movie_rows]
    movie_ids = {movie['id'] for movie in movie_options}
    ticket_movie_rows = (
        db.session.query(Ticket.movie_id, Ticket.movie_title)
        .filter(Ticket.movie_id.isnot(None))
        .distinct()
        .all()
    )
    for movie_id, movie_title in ticket_movie_rows:
        if movie_id not in movie_ids and movie_title:
            movie_options.append({'id': movie_id, 'title': movie_title})
    movie_options.sort(key=lambda item: (item['title'] or '').lower())
    return render_template(
        'admin_tickets.html.j2',
        tickets=tickets,
        movies=movie_options,
        selected_movie_id=movie_id,
        buyer_query=buyer_query,
        booked_date=booked_date_raw,
    )

#for creating admin
@admin_cli.command('create')
def create_admin():
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    admin = User(username=username, email=email, is_admin=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f'Admin account created for {username}')

app.cli.add_command(admin_cli)
####################################################################################################
#CRUD below
# Route to display all products
@app.route('/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.all()
    categories = Category.query.all()  # Fetch categories from the database
    form = ProductForm(categories=categories)  # Pass categories to the form
    return render_template('table.html.j2', products=products, form=form)

# Route to create a new product (Admin only)
@app.route('/products', methods=['POST'])
@login_required
def create_product():
    # Check if the current user is an admin
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403

    # Fetch categories to populate the form
    categories = Category.query.all()
    form = ProductForm(categories=categories)  # Pass categories to the form
    
    if form.validate_on_submit():  # Check if form is valid
        # Create a new product object
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category_id.data
        )
        db.session.add(new_product)  # Add the product to the session
        db.session.commit()  # Commit the session to save it to the database
        flash('Product created successfully!')  # Flash a success message
        return redirect(url_for('get_products'))  # Redirect to the product list after creation

    # If the form is not valid, render the product list with the form
    products = Product.query.all()  # Re-fetch products to display in the table
    return render_template('table.html.j2', products=products, form=form)

# Route to update an existing product (Admin only)
@app.route('/products/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403

    product = Product.query.get_or_404(product_id)

    # Get form data from the request
    product.name = request.form['name']
    product.description = request.form['description']
    product.price = request.form['price']
    product.category_id = request.form['category_id']  # Make sure this matches your form field

    db.session.commit()
    flash('Product updated successfully!')
    return redirect(url_for('view_product', product_id=product.id))

# Route to delete a product (Admin only)
@app.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403
    product = Product.query.get_or_404(product_id)  # Fetch the product
    db.session.delete(product)  # Delete the product
    db.session.commit()  # Commit the changes to the database
    flash('Product deleted successfully!')
    return redirect(url_for('get_products'))  # Redirect to the product list

# Route to view a single product (for all users)
@app.route('/products/<int:product_id>', methods=['GET'])
def view_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html.j2', product=product)

#category
@app.route('/add_category', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can access this
def add_category():
    if not current_user.is_admin:
        flash('You do not have admin access!')
        return redirect(url_for('index'))
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)  # Create a new category object
        db.session.add(new_category)  # Add it to the session
        db.session.commit()  # Commit the session to save it to the database
        flash('Category added successfully!')
        return redirect(url_for('get_products'))  # Redirect to the product list or another page

    return render_template('add_category.html.j2', title="Add Category", form=form)

####################################################################################################
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    # Logic to add the product to the user's cart
    product = Product.query.get_or_404(product_id)  # Fetch the product
    # Assume you have a Cart model to manage the user's cart
    # Example:
    # cart_item = Cart(user=current_user, product=product)
    # db.session.add(cart_item)
    # db.session.commit()

    flash(f'Added {product.name} to your cart!')
    return redirect(url_for('view_product', product_id=product_id))  # Redirect back to the product detail page

###
@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch the product
    categories = Category.query.all()  # Fetch categories for the form

    # Initialize the form with existing product data
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():  # Check if the form is valid
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category_id.data
        db.session.commit()  # Save changes to the database
        flash('Product updated successfully!')
        return redirect(url_for('view_product', product_id=product.id))  # Redirect to the product detail page

    return render_template('edit_product.html.j2', form=form, product=product, categories=categories)  # Pass categories to template



@app.route('/cinema')
def cinema_index():
    movies_db = Movie.query.filter_by(status='now_showing').all()
    movies_vm = [_movie_view_model(m) for m in movies_db]
    return render_template('cinema_index.html.j2', movies=movies_vm)

@app.route('/cinema/movie/<int:movie_id>')
def cinema_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    movie_vm = _movie_view_model(movie, include_showtimes=True)
    sold_seats_by_showtime = {}
    for st in movie.showtimes:
        sold_seats_by_showtime[str(st.id)] = sorted(_get_sold_seats_for_showtime(st))
    return render_template('cinema_movie.html.j2', movie=movie_vm, sold_seats_by_showtime=sold_seats_by_showtime)


@app.route('/api/showtime/<int:showtime_id>/sold_seats', methods=['GET'])
def api_showtime_sold_seats(showtime_id):
    showtime_obj = Showtime.query.get_or_404(showtime_id)
    sold_seats = sorted(_get_sold_seats_for_showtime(showtime_obj))
    return jsonify({'success': True, 'sold_seats': sold_seats})

@app.route('/cinema/coming_soon')
def cinema_coming_soon():
    movies_db = Movie.query.filter_by(status='coming_soon').all()
    movies_vm = [_movie_view_model(m) for m in movies_db]
    return render_template('cinema_coming_soon.html.j2', movies=movies_vm)


# Admin: manage movies
@app.route('/admin/movies')
@login_required
def admin_movies():
    if not current_user.is_admin:
        flash('You do not have admin access!')
        return redirect(url_for('index'))

    movies = Movie.query.order_by(Movie.status, Movie.title).all()
    return render_template('admin_movies.html.j2', movies=movies)


@app.route('/admin/movies/create', methods=['POST'])
@login_required
def admin_create_movie():
    if not current_user.is_admin:
        flash('You do not have admin access!')
        return redirect(url_for('index'))

    title = (request.form.get('title') or '').strip()
    if not title:
        flash('Title is required for a movie.')
        return redirect(url_for('admin_movies'))

    genre = request.form.get('genre') or None
    rating = request.form.get('rating') or None
    status = request.form.get('status') or 'coming_soon'
    poster_url = request.form.get('poster_url') or None
    description = request.form.get('description') or None

    duration = None
    raw_duration = request.form.get('duration')
    if raw_duration:
        try:
            duration = int(raw_duration)
        except ValueError:
            duration = None

    release_date = None
    raw_release = request.form.get('release_date')
    if raw_release:
        try:
            release_date = datetime.strptime(raw_release, '%Y-%m-%d').date()
        except ValueError:
            release_date = None

    movie = Movie(
        title=title,
        genre=genre,
        rating=rating,
        status=status,
        poster_url=poster_url,
        description=description,
        duration=duration,
        release_date=release_date,
    )
    db.session.add(movie)
    db.session.commit()
    flash('Movie created successfully!')
    return redirect(url_for('admin_movies'))


@app.route('/admin/movies/<int:movie_id>', methods=['POST'])
@login_required
def admin_update_movie(movie_id):
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403

    movie = Movie.query.get_or_404(movie_id)
    movie.title = request.form.get('title', movie.title)
    movie.genre = request.form.get('genre', movie.genre)
    movie.rating = request.form.get('rating', movie.rating)
    movie.status = request.form.get('status', movie.status)
    movie.poster_url = request.form.get('poster_url', movie.poster_url)
    db.session.commit()
    flash('Movie updated successfully!')
    return redirect(url_for('admin_movies'))


@app.route('/admin/movies/delete/<int:movie_id>', methods=['POST'])
@login_required
def admin_delete_movie(movie_id):
    if not current_user.is_admin:
        return jsonify({'message': 'Permission denied'}), 403
    movie = Movie.query.get_or_404(movie_id)
    # Clean up related showtimes to avoid NULL foreign keys
    for st in list(movie.showtimes):
        db.session.delete(st)
    db.session.delete(movie)
    db.session.commit()
    flash('Movie deleted successfully!')
    return redirect(url_for('admin_movies'))

@app.route('/cinema/buy_ticket', methods=['POST'])
@login_required
def cinema_buy_ticket():
    movie_id = int(request.form['movie_id'])
    showtime_id = int(request.form['showtime'])
    name = request.form['name']
    email = request.form['email']
    seats = int(request.form['seats'])
    selected_seats = request.form.get('selected_seats', '').strip()  # Get selected seat IDs
    coupon_code = request.form.get('coupon_code', '').strip()  # Get coupon code if provided
    
    movie = Movie.query.get(movie_id)
    showtime_obj = Showtime.query.get(showtime_id)

    if not movie or not showtime_obj:
        flash('電影不存在！', 'error')
        return redirect(url_for('cinema_index'))

    selected_seat_list = _parse_seat_numbers(selected_seats)
    if not selected_seat_list:
        flash('請至少選擇 1 個座位', 'error')
        return redirect(url_for('cinema_movie', movie_id=movie_id))

    if len(selected_seat_list) != len(set(selected_seat_list)):
        flash('座位清單重複，請重新選擇', 'error')
        return redirect(url_for('cinema_movie', movie_id=movie_id))

    sold_seats = _get_sold_seats_for_showtime(showtime_obj)
    conflicted_seats = sorted(set(selected_seat_list).intersection(sold_seats))
    if conflicted_seats:
        flash(f"以下座位已售：{', '.join(conflicted_seats)}", 'error')
        return redirect(url_for('cinema_movie', movie_id=movie_id))

    seats = len(selected_seat_list)
    selected_seats = ','.join(selected_seat_list)

    price_per_ticket = showtime_obj.price if showtime_obj else 100

    # Calculate base price
    base_price = seats * price_per_ticket
    original_price = base_price
    discount_amount = 0
    coupon_used = None
    
    # Apply coupon if provided
    if coupon_code:
        coupon = get_coupon_by_code(coupon_code)
        validation = validate_coupon(coupon, base_price, current_user.id)
        
        if validation['valid']:
            discount_amount = validation['discount']
            base_price = base_price - discount_amount
            coupon_used = coupon
            flash(f'✅ 已應用優惠券！折扣 HK${discount_amount:.2f}', 'success')
        else:
            flash(f'❌ 優惠券無效：{validation["message"]}', 'error')
            # Continue with booking but without coupon
    
    # 創建新的票券記錄
    ticket = Ticket(
        user_id=current_user.id,
        movie_id=movie_id,
        movie_title=movie.title,
        showtime=_format_showtime_label(showtime_obj),
        seats=seats,
        seat_numbers=selected_seats if selected_seats else None,
        original_price=original_price,
        discount_amount=discount_amount,
        total_price=base_price,
        coupon_code=coupon_code if coupon_used else None,
        customer_name=name,
        customer_email=email,
        status='confirmed'
    )
    
    try:
        db.session.add(ticket)
        db.session.commit()
        
        # Mark coupon as used if it was applied
        if coupon_used:
            use_coupon(coupon_used, current_user.id, ticket.id)
        
        # Initialize points if None (for existing users)
        if current_user.points is None:
            current_user.points = 0
        
        # Award points: 1 dollar = 5 points
        # VIP members get +50% bonus points
        base_points = int(base_price * 5)
        if current_user.is_vip:
            points_earned = int(base_points * 1.5)  # 50% bonus
            vip_bonus = points_earned - base_points
        else:
            points_earned = base_points
            vip_bonus = 0
        
        current_user.points += points_earned
        db.session.commit()
        
        # Flash message with VIP bonus info
        if vip_bonus > 0:
            flash(f'✅ 購票成功！獲得 {points_earned} 積分 (含VIP獎勵 +{vip_bonus})', 'success')
        else:
            flash(f'✅ 購票成功！獲得 {points_earned} 積分', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ 購票失敗：{str(e)}', 'error')
        return redirect(url_for('cinema_movie', movie_id=movie_id))
    
    # 將票券信息傳遞給成功頁面
    ticket_info = {
        'id': ticket.id,
        'movie_id': movie_id,
        'movie_title': movie.title,
        'showtime': _format_showtime_label(showtime_obj),
        'name': name,
        'email': email,
        'seats': seats,
        'original_price': original_price,
        'discount_amount': discount_amount,
        'total_price': base_price,
        'coupon_code': coupon_code if coupon_used else None,
        'points_earned': points_earned,
        'total_points': current_user.points
    }
    
    return render_template('cinema_success.html.j2', ticket=ticket_info)

# 我的瀏覽電影頁面
@app.route('/my_movies')
@login_required
def my_movies():
    # 推薦電影列表
    recommended_movies = Movie.query.filter_by(status='now_showing').limit(6).all()
    return render_template('my_movies.html.j2', movies=recommended_movies)

# 我的訂票記錄頁面
@app.route('/my_bookings')
@login_required
def my_bookings():
    # 從數據庫獲取當前用戶的訂票記錄
    user_tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.booking_date.desc()).all()
    
    # 將 Ticket 對象轉換為字典格式以供模板使用
    bookings = []
    for ticket in user_tickets:
        bookings.append({
            'id': ticket.id,
            'movie_id': ticket.movie_id,
            'movie_title': ticket.movie_title,
            'showtime': ticket.showtime,
            'seats': ticket.seats,
            'original_price': ticket.original_price if ticket.original_price else ticket.total_price,
            'discount_amount': ticket.discount_amount if ticket.discount_amount else 0,
            'total_price': ticket.total_price,
            'coupon_code': ticket.coupon_code,
            'name': ticket.customer_name,
            'email': ticket.customer_email,
            'booking_date': ticket.booking_date,
            'status': ticket.status
        })
    
    return render_template('my_bookings.html.j2', bookings=bookings)

# 退票功能
@app.route('/cancel_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # 確保只有票券擁有者可以取消
    if ticket.user_id != current_user.id:
        flash('您無權取消此訂單！', 'error')
        return redirect(url_for('my_bookings'))
    
    # 檢查票券狀態
    if ticket.status == 'cancelled':
        flash('此訂單已經被取消！', 'error')
        return redirect(url_for('my_bookings'))
    
    try:
        # 更新狀態為已取消
        ticket.status = 'cancelled'
        db.session.commit()
        flash(f'已成功取消《{ticket.movie_title}》的訂票！退款將在 3-5 個工作天內處理。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'取消訂票失敗：{str(e)}', 'error')
    
    return redirect(url_for('my_bookings'))

# 我的優惠券頁面
@app.route('/my_coupons')
@login_required
def my_coupons():
    # Get user's coupons from database
    user_coupons = get_user_coupons(current_user.id, include_used=True)
    
    # Format coupons for template
    coupons = []
    for coupon in user_coupons:
        coupon_info = get_coupon_info(coupon)
        template = COUPON_TYPES.get(coupon.coupon_type, {})
        
        # Format discount display
        if template.get('discount_type') == 'percentage':
            discount_display = f"{template.get('discount_value')}% OFF"
        else:
            discount_display = f"HK${template.get('discount_value')}"
        
        coupons.append({
            'id': coupon.id,
            'name': coupon_info['name'],
            'discount': discount_display,
            'code': coupon.code,
            'expiry': coupon.expiry_date.strftime('%Y-%m-%d'),
            'status': 'used' if coupon.is_used else ('expired' if coupon.is_expired else 'available'),
            'description': coupon_info['description'],
            'icon': coupon_info['icon'],
            'days_remaining': coupon_info['days_remaining']
        })
    
    return render_template('my_coupons.html.j2', coupons=coupons)

# 積分兌換優惠券頁面
@app.route('/exchange_points')
@login_required
def exchange_points():
    # Initialize points if None (for existing users)
    if current_user.points is None:
        current_user.points = 0
        db.session.commit()
    
    # Get available coupons for points exchange
    points_coupons = get_points_coupons()
    
    # Format for template
    exchange_options = []
    for coupon_type, template in points_coupons.items():
        if template.get('discount_type') == 'percentage':
            discount_display = f"{template.get('discount_value')}% OFF"
        else:
            discount_display = f"HK${template.get('discount_value')}"
        
        exchange_options.append({
            'type': coupon_type,
            'name': template['name'],
            'description': template['description'],
            'icon': template['icon'],
            'discount': discount_display,
            'points_cost': template['points_cost'],
            'min_purchase': template.get('min_purchase', 0),
            'can_afford': current_user.points >= template['points_cost']
        })
    
    # Sort by points cost
    exchange_options.sort(key=lambda x: x['points_cost'])
    
    return render_template('exchange_points.html.j2', 
                         exchange_options=exchange_options,
                         user_points=current_user.points)

# 處理積分兌換
@app.route('/exchange_points/<coupon_type>', methods=['POST'])
@login_required
def do_exchange_points(coupon_type):
    result = exchange_points_for_coupon(current_user, coupon_type)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('exchange_points'))

# VIP會籍頁面
@app.route('/vip_membership')
@login_required
def vip_membership():
    # Initialize points if None
    if current_user.points is None:
        current_user.points = 0
        db.session.commit()
    
    # Check current VIP status
    vip_status = {
        'is_vip': current_user.is_vip,
        'vip_type': current_user.vip_type,
        'vip_expiry': current_user.vip_expiry.strftime('%Y-%m-%d') if current_user.vip_expiry else None
    }
    
    return render_template('vip_membership.html.j2', 
                         vip_status=vip_status,
                         user_points=current_user.points,
                         membership_level=current_user.membership_level,
                         membership_level_name=current_user.membership_level_name)

# 購買VIP會籍
@app.route('/purchase_vip/<vip_type>', methods=['POST'])
@login_required
def purchase_vip(vip_type):
    from datetime import datetime, timedelta
    
    if vip_type not in ['monthly', 'yearly']:
        flash('❌ 無效的VIP類型', 'error')
        return redirect(url_for('vip_membership'))
    
    # Check if user already has the same VIP type
    if current_user.is_vip and current_user.vip_type == vip_type:
        flash('❌ 您已經擁有此類型的VIP會籍，無需重複購買', 'error')
        return redirect(url_for('vip_membership'))
    
    # Get auto-renew preference from form
    auto_renew = request.form.get('auto_renew') == 'on'
    
    # Set price
    price = 188 if vip_type == 'monthly' else 888
    
    # Calculate expiry date
    if current_user.vip_expiry and current_user.vip_expiry > datetime.utcnow():
        # Extend existing VIP
        base_date = current_user.vip_expiry
    else:
        # New VIP or expired
        base_date = datetime.utcnow()
    
    if vip_type == 'monthly':
        new_expiry = base_date + timedelta(days=30)
    else:  # yearly
        new_expiry = base_date + timedelta(days=365)
    
    # Update user VIP status
    current_user.vip_type = vip_type
    current_user.vip_expiry = new_expiry
    current_user.auto_renew_vip = auto_renew
    
    try:
        db.session.commit()
        # Redirect to VIP confirmation page
        return redirect(url_for('vip_purchase_success', vip_type=vip_type, price=price))
    except Exception as e:
        db.session.rollback()
        flash(f'❌ 購買失敗：{str(e)}', 'error')
        return redirect(url_for('vip_membership'))

# VIP購買成功頁面
@app.route('/vip_purchase_success')
@login_required
def vip_purchase_success():
    vip_type = request.args.get('vip_type')
    price = request.args.get('price')
    
    if not vip_type or not current_user.is_vip:
        flash('❌ 無效的訪問', 'error')
        return redirect(url_for('vip_membership'))
    
    vip_info = {
        'vip_type': vip_type,
        'vip_type_name': '月費會員' if vip_type == 'monthly' else '年費會員',
        'price': price,
        'expiry_date': current_user.vip_expiry,
        'auto_renew': current_user.auto_renew_vip,
        'points_bonus': '50%'
    }
    
    return render_template('vip_success.html.j2', vip_info=vip_info)

# 修改個人資料頁面
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        try:
            # 獲取表單數據
            new_username = request.form.get('username', '').strip()
            new_email = request.form.get('email', '').strip()
            new_phone = request.form.get('phone', '').strip()
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # 驗證用戶名
            if new_username and new_username != current_user.username:
                # 檢查用戶名是否已存在
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    db.session.rollback()  # 回滾任何未提交的更改
                    flash('用戶名已被使用，請選擇其他用戶名！', 'error')
                    return redirect(url_for('edit_profile'))
            
            # 驗證郵箱
            if new_email and new_email != (current_user.email if hasattr(current_user, 'email') else ''):
                # 檢查郵箱是否已存在
                existing_email = User.query.filter_by(email=new_email).first()
                if existing_email and existing_email.id != current_user.id:
                    db.session.rollback()  # 回滾任何未提交的更改
                    flash('電子郵件已被使用，請使用其他郵箱！', 'error')
                    return redirect(url_for('edit_profile'))
            
            # 處理密碼更改驗證（在修改任何數據之前）
            if new_password:
                # 驗證新密碼長度
                if len(new_password) < 8:
                    db.session.rollback()
                    flash('新密碼必須至少 8 個字元！', 'error')
                    return redirect(url_for('edit_profile'))
                
                # 驗證密碼確認
                if new_password != confirm_password:
                    db.session.rollback()
                    flash('新密碼與確認密碼不符！', 'error')
                    return redirect(url_for('edit_profile'))
                
                # 驗證當前密碼（如果有設置的話）
                if current_password and not current_user.check_password(current_password):
                    db.session.rollback()
                    flash('目前密碼錯誤！', 'error')
                    return redirect(url_for('edit_profile'))
            
            # 所有驗證通過後才開始修改數據
            # 更新用戶名
            if new_username and new_username != current_user.username:
                current_user.username = new_username
            
            # 更新郵箱
            if new_email and new_email != (current_user.email if hasattr(current_user, 'email') else ''):
                if hasattr(current_user, 'email'):
                    current_user.email = new_email
            
            # 更新手機號碼
            if hasattr(current_user, 'phone'):
                current_user.phone = new_phone
            
            # 更新密碼
            if new_password:
                current_user.set_password(new_password)
            
            # 提交更改
            db.session.commit()
            flash('個人資料已成功更新！', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗：{str(e)}', 'error')
            return redirect(url_for('edit_profile'))
    
    return render_template('edit_profile.html.j2')


# ==========================================================
# COUPON API ROUTES
# Purpose: AJAX endpoints for coupon validation
# ==========================================================

@app.route('/api/validate_coupon', methods=['POST'])
@login_required
def api_validate_coupon():
    """
    Validate coupon code via AJAX
    Returns JSON with validation result
    """
    data = request.get_json()
    coupon_code = data.get('coupon_code', '').strip().upper()
    order_total = float(data.get('order_total', 0))
    
    if not coupon_code:
        return jsonify({
            'valid': False,
            'message': '請輸入優惠券代碼'
        })
    
    # Get coupon from database
    coupon = get_coupon_by_code(coupon_code)
    
    # Validate coupon
    result = validate_coupon(coupon, order_total, current_user.id)
    
    if result['valid']:
        # Get coupon info for display
        coupon_info = get_coupon_info(coupon)
        
        return jsonify({
            'valid': True,
            'message': '✅ 優惠券有效！',
            'discount': result['discount'],
            'new_total': order_total - result['discount'],
            'coupon_name': coupon_info['name'],
            'coupon_description': coupon_info['description']
        })
    else:
        return jsonify({
            'valid': False,
            'message': f'❌ {result["message"]}'
        })


@app.route('/api/get_user_coupons', methods=['GET'])
@login_required
def api_get_user_coupons():
    """
    Get available coupons for current user
    Returns JSON list of coupons
    """
    print(f"[DEBUG] api_get_user_coupons called by user {current_user.id}")
    
    # Get only valid coupons
    user_coupons = get_user_coupons(current_user.id, include_used=False)
    print(f"[DEBUG] Found {len(user_coupons)} coupons for user")
    
    coupons_data = []
    for coupon in user_coupons:
        coupon_info = get_coupon_info(coupon)
        template = COUPON_TYPES.get(coupon.coupon_type, {})
        
        coupon_dict = {
            'code': coupon.code,
            'name': coupon_info['name'],
            'description': coupon_info['description'],
            'icon': coupon_info['icon'],
            'discount_type': coupon_info.get('discount_type'),
            'discount_value': coupon_info.get('discount_value', 0),
            'min_purchase': coupon_info.get('min_purchase', 0),
            'expiry_date': coupon.expiry_date.strftime('%Y-%m-%d'),
            'days_remaining': coupon_info['days_remaining']
        }
        coupons_data.append(coupon_dict)
        print(f"[DEBUG] Added coupon: {coupon.code} - {coupon_info['name']}")
    
    result = {
        'success': True,
        'coupons': coupons_data,
        'count': len(coupons_data)
    }
    print(f"[DEBUG] Returning {len(coupons_data)} coupons")
    return jsonify(result)

