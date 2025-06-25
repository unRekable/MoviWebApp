from flask import Flask, render_template, request
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

@app.cli.command("init-db")
def init_db_command():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

        existing_user = User.query.filter_by(name="Johannes").first()
        if not existing_user:
            user = data_manager.create_user("Johannes")
            print(f"Initial user 'Johannes' created with ID {user.id}.")
        else:
            user = existing_user
            print("User 'Johannes' already exists.")

        new_movie_data = Movie(name="The Matrix", director="Wachowskis", year=1999,
                               poster_url="https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_SX300.jpg",
                               user_id=user.id)

        existing_movie = Movie.query.filter_by(name=new_movie_data.name, user_id=user.id).first()
        if not existing_movie:
            data_manager.add_movie(new_movie_data)
            print(f"Movie added: {new_movie_data.name} for user {user.name}")
        else:
            print(f"Movie '{new_movie_data.name}' already exists for user '{user.name}'.")

@app.route('/')
def home():
    return "Welcome to MoviWeb App!"

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = data_manager.get_users()
        user_names = [user.name for user in users]
        return user_names
    elif request.method == 'POST':
        return

@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies(user_id):
    if request.method == 'GET':
        # When you click on a user name, the app retrieves that user’s list of favorite movies and displays it.
        movies = data_manager.get_movies(user_id)
        return movies
    elif request.method == 'POST':
        # Add a new movie to a user’s list of favorite movies.
        return

@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def movie_update(user_id, movie_id):
    if request.method == 'POST':
        data_manager.update_movie(user_id, movie_id)

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def movie_delete(user_id, movie_id):
    if request.method == 'POST':
        data_manager.delete_movie(movie_id)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

