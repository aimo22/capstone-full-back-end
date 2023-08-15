from flask import Flask
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager

load_dotenv()

mongo_client = MongoClient(os.environ.get("MONGO_URI"))
db = mongo_client['rescue-db']
user_collection = db['user']

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)

    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    jwt = JWTManager(app)

    app.config['CORS_HEADERS'] = 'Content-Type'

    from .routes.proxy_server_routes import proxy_bp
    from .routes.user_routes import user_bp

    app.register_blueprint(proxy_bp)
    app.register_blueprint(user_bp)

    return app
