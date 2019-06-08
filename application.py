import os
import time
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user
from flask import session as login_session
from search_movie import search_movie
from wtform_fields import *
from models import *
from models import db as d

# Configure app
app = Flask(__name__)
app.secret_key="sdfdsuperfdlkngflkjnlkbgirlsdessexyasspussyfuchyah!!!!!dfghhm;glhjkhjl,.jk"
app.config['WTF_CSRF_SECRET_KEY'] = "b'f\xfa\x8b{X\x8b\x9eM\x83l\x19\xad\x84\x08\xaa"

# Configure database
app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# from app import db
db = SQLAlchemy(app)
# db.metadata.bind = main.db.engine

# Initialize login manager
login = LoginManager(app)
login.init_app(app)

# manage a database connection
# To avaid time errors
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
    d.session.remove()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# socketio = SocketIO(app, manage_session=False)
#
# # Predefined rooms for chat
# ROOMS = ["lounge", "news", "games", "coding"]


@app.route("/register", methods=['GET', 'POST'])
def index():

    reg_form = RegistrationForm()

    # Update database if validation success
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        # Hash password
        hashed_pswd = pbkdf2_sha256.hash(password)

        # Add username & hashed password to DB
        user = User(username=username, hashed_pswd=hashed_pswd)
        db.session.add(user)
        db.session.commit()
        db.session.remove()

        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    # Allow login if validation success
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        # return redirect(url_for('chat'))
        login_session['user_id'] = user_object.id
        db.session.remove()
        return redirect(url_for('showCatalog'))


    return render_template("login.html", form=login_form)


@app.route("/logout", methods=['GET'])
def logout():
    # Logout user
    logout_user()
    # del login_session['user_id']
    flash('You have logged out successfully', 'success')
    return redirect(url_for('showCatalog'))


# @app.route("/chat", methods=['GET', 'POST'])
# def chat():
#
#     if not current_user.is_authenticated:
#         flash('Please login', 'danger')
#         return redirect(url_for('login'))
#
#     return render_template("chat.html", username=current_user.username, rooms=ROOMS)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

# Using this function to get info from search_movie
def getMovieInf(movieName):
    movie = search_movie(movieName)
    # if movie found return the info about it
    if movie:
        overview = movie[0]
        trailer = movie[1]
        poster = movie[2]
        return trailer, overview, poster
    return False


@app.route('/')
@app.route('/catalogs')
def showCatalog():
    catalogs = Catalog.query.all()
    if not current_user.is_authenticated:
        return render_template('catalogs.html', catalogs=catalogs)
    else:
        return render_template('catalogsloggedin.html', catalogs=catalogs)


@app.route('/catalogs/<catalog_name>')
@app.route('/catalogs/<catalog_name>/movies')
def showItem(catalog_name):
    poster = []
    catalogs = Catalog.query.all()
    catalog_id = Catalog.query.filter_by(name=catalog_name).first().id
    catalog = Catalog.query.filter_by(name=catalog_name).one()

    # Check if the user in login session
    # return the movies thay belong to each user
    if 'user_id' in login_session:
        user_id = login_session['user_id']
        items = (Item.query
                 .filter_by(catalog_id=catalog.id)
                 .filter_by(user_id=user_id)
                 .all()
                 )
    # If not just return the welcome page
    else:
        items = (Item.query
                 .filter_by(catalog_id=catalog.id)
                 .all()
                 )
        return render_template('welcome.html', catalogs=catalogs)

    # To avoid errors check if thier items found
    # get the movie info and create a list of poster
    # pass this poster list to template to display it
    # items = (Item.query
    #         .filter_by(catalog_id=catalog.id)
    #         .all()
    #              )
    if items:
        for item in items:
            movie = getMovieInf(item.name)
            poster.append(movie[2])

    if not current_user.is_authenticated:
        return render_template('items.html', items=items, catalog=catalog,
                               catalogs=catalogs, catalog_name=catalog_name,
                               x=len(items), poster=poster)
    else:
        return render_template('itemsloggedin.html',
                               items=items, catalog=catalog,
                               catalogs=catalogs, catalog_name=catalog_name,
                               x=len(items), poster=poster)


@app.route('/catalogs/<catalog_name>/<item_name>')
def showItemInfo(catalog_name, item_name):
    # Using moviesDB to get the info
    movie = getMovieInf(item_name)
    catalogs = Catalog.query.all()
    items = Item.query.filter_by(name=item_name).first()
    catalog = Catalog.query.filter_by(id=items.catalog_id).first()
    db.session.remove()
    # Check if info found
    # then, get trailer and overview
    if movie:
        # Get the overview
        overview = movie[1]
        # Pass the key to youtube embed to show the trailer
        m = movie[0]
    if not current_user.is_authenticated:
        return render_template('itemInfo.html', items=items,
                               overview=overview, m=m, catalogs=catalogs)
    else:
        return render_template('itemInfologgedin.html',
                               items=items,overview=overview,
                               m=m, catalogs=catalogs)


@app.route('/catalogs/<catalog_name>/movies/new', methods=['GET', 'POST'])
def newItem(catalog_name):
    if not current_user.is_authenticated:
        # catalogs = session.query(Catalog).all()
        catalogs = Catalog.query.all()
        flash("You are not loggged in!" )
        db.session.remove()
        return render_template('notAuthorized.html', catalogs=catalogs)
    # catalog_id = session.query(Catalog).filter_by(name=catalog_name).first().id
    catalog_id = Catalog.query.filter_by(name=catalog_name).first().id
    if request.method == 'POST':
        # Check if the movie exsit
        # Or user type the movie name incorrectly
        if getMovieInf(request.form['name']):
            # Get discription and save it in DB
            description = 'No description for this movie'
            if getMovieInf(request.form['name'])[2]:
                description = getMovieInf(request.form['name'])[2]
            newItem = Item(name=request.form['name'], description=description,
                           type=catalog_name, catalog_id=catalog_id,
                           user_id=login_session['user_id'])

            db.session.add(newItem)
            db.session.commit()
            db.session.remove()
            flash("New Movie added!")
            return redirect(url_for('showItem', catalog_name=catalog_name))
        # Notify the user
        else:
            flash("This movie is not exist :( , please check your spelling!")
            return redirect(url_for('newItem', catalog_name=catalog_name))
    else:
        return render_template('newItem.html', catalog_name=catalog_name)


@app.route('/catalogs/<catalog_name>/<item_name>/edit',
           methods=['GET', 'POST'])
def editItem(catalog_name, item_name):
    # catalogs = session.query(Catalog).all()
    catalogs = Catalog.query.all()
    if not current_user.is_authenticated:
        flash("You are not loggged in!" )
        db.session.remove()
        return render_template('notAuthorized.html', catalogs=catalogs)

    editedItem = (Item.query.filter_by(user_id=login_session['user_id'])
                                     .filter_by(name=item_name)
                                     .first()
                                     )
    if login_session['user_id'] != editedItem.user_id:
        flash('''You are not authorized to update the movies list,
              Please login first!''')
        return render_template('notAuthorized.html', catalogs=catalogs)

    if request.method == 'POST':
        # if name changed updatemthe movie name in database
        if request.form['name']:
            editedItem.name = request.form['name']
            # db.session.add(editedItem)
            db.session.merge(editedItem)
            db.session.commit()
            db.session.remove()

        # if genre changed, update the movie type in DB
        if request.form['genre'] != 'Choose...':
            editedCatalog = str(request.form.get('genre'))
            # editedItem.type = editedCatalog
            catalog_id = (Catalog.query
                          .filter_by(name=editedCatalog)
                          .first()
                          .id
                          )
            editedItem.catalog_id = catalog_id
            db.session.merge(editedItem)
            db.session.commit()
            db.session.remove()

        # db.session.add(editedItem)
        # db.session.commit()
        flash("Movie has been edited!")
        return redirect(url_for('showItem', catalog_name=catalog_name))
    else:
        return render_template('editItem.html', item_name=item_name,
                               catalogs=catalogs, catalog_name=catalog_name,
                               item=editedItem)


@app.route('/delete', methods=['POST'])
def editTask():
    item_name = request.args.get('name')
    item = (Item.query.filter_by(user_id=login_session['user_id'])
            .filter_by(name=item_name)
            .first()
            )
    if current_user.is_authenticated:
        d.session.delete(item)
        d.session.commit()
        return jsonify({'result': 'success'})


# @app.route('/catalogs/<catalog_name>/<item_name>/delete',
#            methods=['GET', 'POST'])
# def deleteItem(catalog_name, item_name):
#     # catalogs = session.query(Catalog).all()
#     catalogs = Catalog.query.all()
#     if not current_user.is_authenticated:
#         flash("You are not loggged in!" )
#         return render_template('notAuthorized.html', catalogs=catalogs)
#     item = (Item.query.filter_by(user_id=login_session['user_id'])
#                                .filter_by(name=item_name)
#                                .first()
#                                )
#     if login_session['user_id'] != item.user_id:
#         flash('''You are not authorized to update the movies list,
#               Please login first!''' )
#         return render_template('notAuthorized.html', catalogs=catalogs)
#
#     if request.method == 'POST':
#         d.session.delete(item)
#         d.session.commit()
#         db.session.remove()
#         flash("Movie has been deleted!")
#         return redirect(url_for('showItem', catalog_name=catalog_name))
#     else:
#         return render_template('deleteItem.html',
#                                item_name=item_name, catalog_name=catalog_name,
#                                item=item)

if __name__ == "__main__":
    app.run(debug=True)
