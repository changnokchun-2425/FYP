from flask import render_template, redirect, flash, url_for, request, jsonify, make_response
from flask_login import login_required, current_user, login_user, logout_user 
from urllib.parse import urlparse
from flask.cli import AppGroup

from app import app, db
from app.forms import LoginForm, RegistrationForm, ProductForm, CategoryForm
from app.models import User, Category, Product, Article, Comment, Tag, ArticleTag, Source, Reaction, Author, Newsletter
admin_cli = AppGroup('admin')

@app.route("/")
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
    return render_template("profile.html.j2", title="Profile", user=user)

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
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('admin_login.html.j2', title="Admin Sign In", form=form)

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

