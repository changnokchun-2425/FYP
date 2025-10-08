import re
import sys
import requests

SESSION = requests.Session()
BASE = 'http://127.0.0.1:5000'

try:
    r = SESSION.get(BASE + '/register', timeout=5)
    r.raise_for_status()
    html = r.text
    m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    token = m.group(1) if m else None
    print('CSRF token:', token)

    data = {
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'password': 'password',
        'password2': 'password',
        'csrf_token': token,
        'submit': 'Register'
    }

    r2 = SESSION.post(BASE + '/register', data=data, allow_redirects=False, timeout=5)
    print('POST status:', r2.status_code)
    if r2.is_redirect:
        print('Redirect to:', r2.headers.get('Location'))
    else:
        print('Response length:', len(r2.text))

except Exception as e:
    print('Error during test:', e)
    sys.exit(1)

print('Done')
