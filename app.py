from flask import Flask
from models import db, User, Movie
from data_manager import DataManager
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

data_manager = DataManager()

user = data_manager.create_user("Alice")
movies = data_manager.get_movies(user.id)

with app.app_context():
    db.create_all()