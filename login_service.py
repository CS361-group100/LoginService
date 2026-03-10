import os
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
password_hasher = Bcrypt(app)

    # --- QUALITY ATTRIBUTE: Rate Limiting (Story 1) ---
redis_url = os.getenv("REDIS_URL", "memory://")
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
#    default_limits=["5 per 1 minutes"],
    storage_uri=redis_url,
    strategy="fixed-window"
)

    # Thread lock to satisfy Quality Attribute: Data Integrity (Story 2)
    # This prevents race conditions where two users register the same name simultaneously.
registration_lock = threading.Lock()
    # Mock Database
users_db = []
    # Initialize dictionary to track login attempts.
login_attempts = {}
    # Set lockout period to 20 minutes.
LOCKOUT_PERIOD = timedelta(minutes=20)

    # the limiter was exceeded and returned a 429 code
@app.errorhandler(429)
def ratelimit_handler(e):
    """Acceptance Criteria (Story 1): Return 429 and specific message."""
    return make_response(
        jsonify(error="too_many_requests", message="Retry after 20 minutes"),
        429
    )


    # --- USER STORY 2 & 3: New User/Create Account & Password Length ---
@app.route('/auth/register', methods=['POST'])
def register():

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

        # Acceptance Criteria (Story 3): Password Length Constraint
        # Checks that a password was entered and that it is 10 or more digits
    if not password or len(password) < 10:
        return jsonify({
            "error": "bad_request",
            "message": "Password length must be 10 or more characters"
        }), 400

#Prevents simultaneous creation of same username.
    with registration_lock:
        if any(u['username'] == username for u in users_db):
            return jsonify({
                "error": "conflict",
                "message": "Username already in use"
            }), 409

            # Quality Attribute (Story 3): Security (Hashing)
            # Converts the entered password into a hashed password
        hashed_pw = password_hasher.generate_password_hash(password).decode(
            'utf-8')
            # Creates a new user object.
        new_user = {
            "userId": len(users_db) + 1,
            "username": username,
            "password": hashed_pw,
            "displayName": "User"
        }
            # Stores the user object into the user_db list.
        users_db.append(new_user)

        # Acceptance Criteria (Story 2): Success Code 201
    return jsonify({"message": "User created. Please sign in."}), 201


    # --- USER STORY 1: Sign In ---
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

# Check if the user is currently locked out
    if username in login_attempts:
        attempts = login_attempts[username]
        lockout_until = attempts.get("lockout_until")  # might be None

        if lockout_until is not None and lockout_until > datetime.now():
            return jsonify(
                error="You are blocked from logging in for 20 minutes."
            ), 403
        # Cycles through the list ('users_db') of objects (users) to check
        # if one of the objects has a 'username' that matches the input
        # username. Returns the username object if found, None if not.
    user = next((u for u in users_db if u['username'] == username), None)

    # If user is not None and the password for the returned user object
    # matches the input password then return a "user" object, an access
    # token and the code 200.
    # Acceptance Criteria (Story 1): 200 OK on success
    if user and password_hasher.check_password_hash(user['password'],
                                                    password):
            # Reset login attempts on successful login
        if username in login_attempts:
            del login_attempts[username]

        return jsonify({
            "user": {
                "userId": user["userId"],
                "username": user["username"],
                "displayName": user["displayName"]
            },
            "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example_token"
        }), 200

        # Increase failed attempts as the username or password was incorrect .
    if username not in login_attempts:
        login_attempts[username] = {'count': 0, 'lockout_until': None}

    login_attempts[username]['count'] += 1

        # Lock user out if more than 5 attempts
    if login_attempts[username]['count'] > 5:
        login_attempts[username]['lockout_until'] = datetime.now() + LOCKOUT_PERIOD
        return jsonify(
            error="Too many failed attempts. You are blocked from logging in for 20 minutes."
        ), 403

    return jsonify({
        "error": "INVALID_CREDENTIALS",
        "message": "Email or password is incorrect."
    }), 401


if __name__ == '__main__':
    app.run(debug=True)
