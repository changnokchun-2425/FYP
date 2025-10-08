from app import app, db
from app.models import User


def setup_db():
    with app.app_context():
        db.create_all()
        # create an admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print('Created admin user (username=admin, password=admin)')
        else:
            print('Admin user already exists')


if __name__ == '__main__':
    setup_db()
