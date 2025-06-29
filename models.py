from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    User model representing a user in the application.
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the User object.
        """
        return self.name


class Movie(db.Model):
    """
    Movie model representing a movie entry.
    """
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    director = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref='movies', lazy=True)

    def __repr__(self):
        """
        Returns a string representation of the Movie object.
        """
        return '<Movie %r>' % self.name
