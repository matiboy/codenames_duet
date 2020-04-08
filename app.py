import logging
import sys
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from itsdangerous.url_safe import URLSafeSerializer
from config import Config
from flask_jwt_extended import JWTManager

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
signer = URLSafeSerializer(Config.SECRET)
jwt = JWTManager(app)
