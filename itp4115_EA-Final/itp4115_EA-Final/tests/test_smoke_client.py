import os
import sys

# Ensure project root is on sys.path so `import app` works when running this file directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app, db
from app.models import User


def run_smoke_tests():
    # Disable CSRF for testing convenience
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

        # Register a new user
        rv = client.post('/register', data={
            'username': 'smoketest',
            'email': 'smoketest@example.com',
            'password': 'password',
            'password2': 'password',
        }, follow_redirects=True)
        print('Register status code:', rv.status_code)
        if b'Congraduations' in rv.data:
            print('Register appears successful')
        else:
            print('Register response length:', len(rv.data))

        # Login as admin (created by create_db.py earlier)
        rv2 = client.post('/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
        print('Login status code:', rv2.status_code)
        if b'Home' in rv2.data or rv2.status_code == 200:
            print('Login request returned OK')
        else:
            print('Login response length:', len(rv2.data))


if __name__ == '__main__':
    run_smoke_tests()
