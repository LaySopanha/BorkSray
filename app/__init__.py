from flask import Flask
from .routes import main  # Import the main blueprint correctly

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)  # Register the blueprint

    return app
