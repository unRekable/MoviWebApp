from flask import Flask, render_template, request, jsonify
from models import db, User, Movie
from data_manager import DataManager
from api_handler import get_movie_by_title
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
    users = data_manager.get_users()
    return render_template('index.html', users=users)
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = data_manager.get_users()
        user_names = [user.name for user in users]
        return user_names
    elif request.method == 'POST':
        user = request.form.get('name')
        if user:
            data_manager.create_user(user)
            return f"{user} created successfully.", 200

@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies(user_id):
    if request.method == 'GET':
        movies = data_manager.get_movies(user_id)
        if not movies:
            return "No movies found.", 404

        return render_template('movies.html', movies=movies)

    elif request.method == 'POST':
        movie = request.form.get('movie')
        if movie:
            movies_dict = get_movie_by_title(movie)

            title = movies_dict['Title']
            year = movies_dict['Year']
            director = movies_dict['Director']
            poster_url = movies_dict['Poster']

            new_movie_data = Movie(name=title, director=director, year=year, poster_url=poster_url, user_id=user_id)
            existing_movie = Movie.query.filter_by(name=new_movie_data.name, user_id=user_id).first()

            if not existing_movie:
                data_manager.add_movie(new_movie_data)
                return f"Movie added: {new_movie_data.name} for user.", 200
            else:
                return f"Movie '{new_movie_data.name}' already exists for user."

@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def movie_update(user_id, movie_id):
    if request.method == 'POST':
        movie_title = request.form.get('title')

        if not movie_title:
            return "No movie title provided.", 404

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404

        if data_manager.update_movie(movie_id, movie_title):
            return f"Movie updated successfully", 200
        else:
            return jsonify({"error": f"Movie '{movie_title}' not found."}), 404

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def movie_delete(user_id, movie_id):
    if request.method == 'POST':

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404

        if data_manager.delete_movie(movie_id):
            return "Movie deleted successfully", 200
        else:
            return "Movie not found or could not be deleted.", 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)

