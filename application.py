"""
Flask Item Catalog — application entry point.

Creates the Flask app, registers the two route blueprints, and starts
the development server when run directly.

    python application.py
"""

import os

from flask import Flask

from auth import auth_bp
from views import catalog_bp

# Allows OAuth redirect URIs to use plain HTTP on localhost.
# Remove this line (or set to "0") when deploying over HTTPS.
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "catalog-dev-secret-change-in-prod")

# Register route modules as Blueprints so each file owns its own routes.
app.register_blueprint(auth_bp)
app.register_blueprint(catalog_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
