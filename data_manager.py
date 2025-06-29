class DataManager:
    """
    Manages database operations for User and Movie models.
    """

    def create_user(self, name):
        """
        Creates a new user in the database.

        Args:
            name (str): The name of the user.

        Returns:
            User: The newly created User object.
        """
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self):
        """
        Retrieves all users from the database.

        Returns:
            list[User]: A list of all User objects.
        """
        return User.query.all()

    def get_movies(self, user_id):
        """
        Retrieves all movies associated with a specific user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[Movie]: A list of Movie objects for the given user.
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def add_movie(self, movie):
        """
        Adds a new movie to the database.

        Args:
            movie (Movie): The Movie object to add.

        Returns:
            Movie: The added Movie object.
        """
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id, new_title):
        """
        Updates the title of a specific movie.

        Args:
            movie_id (int): The ID of the movie to update.
            new_title (str): The new title for the movie.

        Returns:
            bool: True if the movie was found and updated, False otherwise.
        """
        movie_to_update = Movie.query.get(movie_id)
        if movie_to_update:
            movie_to_update.name = new_title
            db.session.commit()
            return True
        return False

    def delete_movie(self, movie_id):
        """
        Deletes a movie from the database.

        Args:
            movie_id (int): The ID of the movie to delete.

        Returns:
            bool: True if the movie was found and deleted, False otherwise.
        """
        movie_to_delete = Movie.query.get(movie_id)
        if movie_to_delete:
            db.session.delete(movie_to_delete)
            db.session.commit()
            return True
        return False