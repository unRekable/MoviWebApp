from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, User, Movie
from data_manager import DataManager
from api_handler import get_movie_by_title
import os

app = Flask(__name__)

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'movies.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize SQLAlchemy with the Flask app

data_manager = DataManager()  # Create an instance of your DataManager


# --- CLI Command for Database Initialization ---
@app.cli.command("init-db")
def init_db_command():
    """
    CLI command to initialize the database and populate with initial data.
    Run with 'flask init-db'.
    """
    with app.app_context():
        db.create_all()
        print("Database tables created.")

        # Add initial user 'Johannes' if not exists
        existing_user = User.query.filter_by(name="Johannes").first()
        if not existing_user:
            user = data_manager.create_user("Johannes")
            print(f"Initial user 'Johannes' created with ID {user.id}.")
        else:
            user = existing_user
            print("User 'Johannes' already exists.")

        # Add initial movie 'The Matrix' for 'Johannes' if not exists
        new_movie_data = Movie(
            name="The Matrix",
            director="Wachowskis",
            year=1999,
            poster_url="https://m.media-amazon.com/images/M/MV5BN2NmN2VhMTQtMDNiOS00NDlhLTliMjgtODE2ZTY0ODQyNDRhXkEyXkFqcGc@._V1_SX300.jpg",
            user_id=user.id
        )

        existing_movie = Movie.query.filter_by(name=new_movie_data.name, user_id=user.id).first()
        if not existing_movie:
            data_manager.add_movie(new_movie_data)
            print(f"Movie added: {new_movie_data.name} for user {user.name}")
        else:
            print(f"Movie '{new_movie_data.name}' already exists for user '{user.name}'.")


# --- Routes ---

@app.route('/')
def home():
    """Renders the homepage displaying a list of users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['GET', 'POST'])
def users():
    """
    Handles user creation (POST) and retrieves all user names (GET).
    Returns JSON responses for API-like behavior.
    """
    if request.method == 'GET':
        users = data_manager.get_users()
        user_names = [user.name for user in users]
        return jsonify(user_names), 200  # Return as JSON list
    elif request.method == 'POST':
        user_name = request.form.get('name')
        if not user_name:
            return jsonify({"error": "User name is required."}), 400  # Bad Request

        # Check if user already exists to avoid duplicates
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user:
            return jsonify({"message": f"User '{user_name}' already exists."}), 409  # Conflict

        user = data_manager.create_user(user_name)
        return jsonify({"message": f"User '{user.name}' created successfully.", "user_id": user.id}), 201  # Created


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies(user_id):
    """
    Handles retrieving movies for a specific user (GET) and adding new movies (POST).
    """
    # Check if user exists for any operation
    user = User.query.get(user_id)
    if not user:
        # If the user_id from the URL doesn't exist, return 404 for both GET/POST
        return jsonify({"error": f"User with ID {user_id} not found."}), 404

    if request.method == 'GET':
        movies = data_manager.get_movies(user_id)
        return render_template('movies.html', movies=movies, user=user)

    elif request.method == 'POST':
        movie_title_from_form = request.form.get('title')
        if not movie_title_from_form:
            return jsonify({"error": "Movie title is required."}), 400  # Bad Request

        try:
            # Call external API to get movie details
            movies_dict = get_movie_by_title(movie_title_from_form)

            # Check if API returned actual movie data or an error
            if not movies_dict or movies_dict.get('Response') == 'False':
                return jsonify(
                    {"error": f"Movie '{movie_title_from_form}' not found by API."}), 404  # Not Found from API

            title = movies_dict.get('Title')
            year = movies_dict.get('Year')
            director = movies_dict.get('Director')
            poster_url = movies_dict.get('Poster')

            # Validate essential fields from API response
            if not all([title, year, director, poster_url]):
                return jsonify(
                    {"error": "Missing essential movie data from API response."}), 500  # Internal Server Error

            new_movie_data = Movie(name=title, director=director, year=year, poster_url=poster_url, user_id=user_id)
            existing_movie = Movie.query.filter_by(name=new_movie_data.name, user_id=user_id).first()

            if not existing_movie:
                data_manager.add_movie(new_movie_data)
                return redirect(url_for('movies', user_id=user_id))
            else:
                return jsonify(
                    {"message": f"Movie '{new_movie_data.name}' already exists for user '{user.name}'."}), 409

        except Exception as e:
            # Catch any other exceptions during API call or data processing
            return jsonify(
                {"error": f"An error occurred while adding the movie: {str(e)}"}), 500  # Internal Server Error


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """
    Handles updating an existing movie for a specific user.
    """
    # Check if user exists (already handled in movies_route GET/POST, but good for direct access)
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with ID {user_id} not found."}), 404

    movie_title = request.form.get('title')
    if not movie_title:
        return jsonify({"error": "No movie title provided for update."}), 400  # Bad Request

    # The movie being updated must belong to the user_id in the URL
    movie_to_update = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie_to_update:
        return jsonify({"error": f"Movie with ID {movie_id} not found for user {user.name}."}), 404  # Not Found

    # Check for duplicate movie name for the same user (if update changes name to existing one)
    existing_movie_with_new_title = Movie.query.filter_by(name=movie_title, user_id=user_id).first()
    if existing_movie_with_new_title and existing_movie_with_new_title.id != movie_id:
        return jsonify(
            {"message": f"A movie with title '{movie_title}' already exists for user '{user.name}'."}), 409  # Conflict

    if data_manager.update_movie(movie_id, movie_title):
        return redirect(url_for('movies', user_id=user_id))
    else:
        return jsonify({"error": f"Failed to update movie with ID {movie_id}."}), 500  # Internal Server Error


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Handles deleting a movie for a specific user.
    """
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with ID {user_id} not found."}), 404

    # Ensure the movie to delete actually belongs to the user_id in the URL
    movie_to_delete = Movie.query.filter_by(id=movie_id, user_id=user_id).first()
    if not movie_to_delete:
        return jsonify({"error": f"Movie with ID {movie_id} not found for user {user.name}."}), 404  # Not Found

    if data_manager.delete_movie(movie_id):  # This function will now only be called if movie_to_delete is found
        return redirect(url_for('movies', user_id=user_id))
    else:
        return jsonify({"error": f"Failed to delete movie with ID {movie_id}."}), 500  # Internal Server Error


if __name__ == '__main__':
    app.run(debug=True, port=5000)