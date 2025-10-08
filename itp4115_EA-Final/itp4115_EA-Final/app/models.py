
from datetime import datetime
from app import db, login

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)  # Ensure this line exists
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<Post {self.body}>'
    
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Sale {self.item}>'
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', backref='products')

    def __repr__(self):
        return f'<Product {self.name}>'
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
#############################################################################

class Article(db.Model):
    """Represents a news article."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='articles')
    category = db.relationship('Category', backref='articles')

    def __repr__(self):
        return f'<Article {self.title}>'


class Comment(db.Model):
    """Represents a comment on an article."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    article = db.relationship('Article', backref='comments')
    user = db.relationship('User', backref='comments')

    def __repr__(self):
        return f'<Comment {self.content[:20]}>'


class Tag(db.Model):
    """Represents a tag for articles."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'


class ArticleTag(db.Model):
    """Associative table for many-to-many relationship between articles and tags."""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))

    article = db.relationship('Article', backref='article_tags')
    tag = db.relationship('Tag', backref='article_tags')


class Source(db.Model):
    """Represents the source of a news article."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<Source {self.name}>'


class Reaction(db.Model):
    """Represents user reactions to articles."""
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reaction_type = db.Column(db.String(10))  # e.g., 'like', 'dislike'

    article = db.relationship('Article', backref='reactions')
    user = db.relationship('User', backref='reactions')

    def __repr__(self):
        return f'<Reaction {self.reaction_type} by {self.user_id}>'


class Author(db.Model):
    """Represents an author of articles."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    bio = db.Column(db.Text)

    def __repr__(self):
        return f'<Author {self.name}>'


class Newsletter(db.Model):
    """Represents a newsletter subscription."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Newsletter {self.email}>'