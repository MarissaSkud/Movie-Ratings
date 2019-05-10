"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension


from model import User, Rating, Movie, connect_to_db, db



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route('/users')
def user_list():

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/registration-form')
def show_registration():

    return render_template("registration-form.html")


@app.route('/sign-up', methods=["POST"])
def register():
    """Check if user email exists in database and add them as new user if not"""

    email = request.form['email']
    password = request.form['password']

    match = User.query.filter_by(email=email).all()

    if not match:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template("registration-submitted.html", status="added",
            email=email)

    else:
        return render_template("registration-submitted.html", status="preexisting", 
            email=email)


@app.route('/login-form')
def show_login():

    return render_template("login-form.html") 


@app.route('/login')
def login():
    email = request.args['email']
    password = request.args['password']
    user = User.query.filter_by(email=email).first()

    if password == user.password:
        session['user_id'] = user.user_id

        flash("Login successful")
        return redirect("/")


@app.route('/logout')
def logout():
    session.pop('user_id')

    flash("Logout successful")
    return redirect("/")


@app.route('/users/<user_id>')
def show_user_page(user_id):
    user = User.query.filter_by(user_id=user_id).one()
    age = user.age
    zipcode = user.zipcode
    scored_movies = db.session.query(Rating.score, Movie.title).filter_by(user_id=user_id).join(Movie).all()
    #print(scored_movies, "+++++++++++++++++++++++++++++++++++++++++")

    return render_template("user_page.html", user_id=user_id,
                                             age=age,
                                             zipcode=zipcode,
                                             scored_movies=scored_movies)

@app.route('/movies')
def movie_list():
    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<movie_id>')
def show_movie_page(movie_id):

    movie = Movie.query.filter_by(movie_id=movie_id).one()
    title = movie.title
    released = movie.released_at
    scores = Rating.query.filter_by(movie_id=movie_id).all()

    return render_template("movie_page.html", movie_id=movie_id,
                    title=title, released=released, scores=scores)


@app.route('/rate-movie', methods=["POST"])
def add_rating():

    user_id = session["user_id"]
    movie_id = request.form['movie']
    score = request.form["Rating"]

    rating_lookup = Rating.query.filter_by(user_id=user_id, movie_id=movie_id)

    if not rating_lookup:
        new_rating = Rating(user_id=user_id, movie_id=movie_id, score=score)
        db.session.add(new_rating)
        db.session.commit()

    else:
        rating_lookup.score = score

    flash("Rating added")
    return redirect(f"/movies/{movie_id}")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
