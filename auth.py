"""
Authentication module.

Defines the auth_bp Blueprint and all OAuth 2.0 routes:
  /login      — login page
  /gconnect   — initiates the Google OAuth flow
  /gcallback  — handles the OAuth callback and creates the user session
  /logout     — clears the session

Also exports the login_required decorator used by views.py.
"""

import json
import os
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from database import db_session
from models import User

auth_bp = Blueprint("auth", __name__)

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secrets.json")

# Minimum scopes needed to identify the user — email, name, and profile picture.
GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


# ---------- Public decorator ----------


def login_required(route_func):
    """
    Decorator that redirects unauthenticated users to the login page.

    Apply to any route that requires the user to be signed in.
    """
    @wraps(route_func)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("auth.show_login"))
        return route_func(*args, **kwargs)
    return decorated_function


# ---------- Private helpers ----------


def _find_user_by_email(email):
    """Return the User row matching email, or None if not found."""
    return db_session.query(User).filter_by(email=email).first()


def _create_user(name, email, picture):
    """Insert a new User row and return it."""
    new_user = User(name=name, email=email, picture=picture)
    db_session.add(new_user)
    db_session.commit()
    return new_user


def _load_client_id():
    """Read the Google client ID from the secrets file."""
    with open(CLIENT_SECRETS_FILE) as secrets_file:
        return json.load(secrets_file)["web"]["client_id"]


# ---------- Routes ----------


@auth_bp.route("/login")
def show_login():
    """Display the login page, or redirect home if already authenticated."""
    if "user_id" in session:
        return redirect(url_for("catalog.show_catalog"))
    return render_template("login.html")


@auth_bp.route("/gconnect")
def gconnect():
    """Redirect the user to Google's OAuth 2.0 authorisation endpoint."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=url_for("auth.gcallback", _external=True),
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        # Force account selection so the user can switch Google accounts.
        prompt="select_account",
    )
    # Store the state token in the session to prevent CSRF on the callback.
    session["oauth_state"] = state
    return redirect(authorization_url)


@auth_bp.route("/gcallback")
def gcallback():
    """
    Handle the Google OAuth callback.

    Steps:
    1. Verify the state token to prevent CSRF.
    2. Exchange the authorisation code for credentials.
    3. Verify the ID token issued by Google.
    4. Find or create the matching User row.
    5. Persist the user identity in the Flask session.
    """
    # Reject the callback if the state does not match what was sent to Google.
    if request.args.get("state") != session.get("oauth_state"):
        flash("Invalid OAuth state. Please try logging in again.", "danger")
        return redirect(url_for("auth.show_login"))

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        state=session["oauth_state"],
        redirect_uri=url_for("auth.gcallback", _external=True),
    )

    # Exchange the one-time authorisation code for an access token and ID token.
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Verify the ID token signature and audience against Google's public keys.
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        google_requests.Request(),
        _load_client_id(),
    )

    user = _find_user_by_email(id_info["email"])
    if not user:
        # First login — create a persistent user record.
        user = _create_user(
            name=id_info.get("name", "User"),
            email=id_info["email"],
            picture=id_info.get("picture", ""),
        )

    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_picture"] = user.picture

    flash(f"Welcome, {user.name}!", "success")
    return redirect(url_for("catalog.show_catalog"))


@auth_bp.route("/logout")
def logout():
    """Clear the session and redirect to the catalog homepage."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("catalog.show_catalog"))
