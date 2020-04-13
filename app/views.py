"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

import os
import datetime
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm
from app.models import UserProfile, Use
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from .models import MyForm, PhotoForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        # change this to actually validate the entire form submission
        # and not just one field
        if form.username.data:
            # Get the username and password values from the form.
            password = form.password.data
            username = form.username.data

            # using your model, query database for a user based on the username
            # and password submitted. Remember you need to compare the password hash.
            # You will need to import the appropriate function to do so.
            # Then store the result of that query to a `user` variable so it can be
            # passed to the login_user() method below.
            user = UserProfile.query.filter_by(username=username).first()

            if user is not None and check_password_hash(user.password, password):
                # get user id, load into session
                login_user(user)

                # remember to flash a message to the user
                flash("successfully logged in", 'success')
                return redirect(url_for("secure_page"))  # they should be redirected to a secure-page route instead
    return render_template("login.html", form=form)


@app.route("/secure-page")
@login_required
def secure_page():
    return render_template('secure_page.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('home'))


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    myform = MyForm()

    if request.method == 'POST' and myform.validate_on_submit():
        firstname = myform.firstname.data
        lastname = myform.lastname.data
        gender = myform.gender.data
        email = myform.email.data
        location = myform.location.data
        bio = myform.bio.data
        photo = myform.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))
        d = datetime.datetime.today()
        dates = d.strftime("%d-%B-%Y")

        user = Use(first_name=firstname, last_name=lastname, gender=gender, email=email, location=location, bio=bio,
                   photo=filename, dates=dates)

        db.session.add(user)
        db.session.commit()

        users = Use.query.all()

        flash('You have successfully filled out the form', 'success')
        return render_template('profiles.html', filename=filename, firstname=firstname, lastname=lastname, gender=gender, location=location, users=users)

    return render_template('add_profile.html', form=myform)


@app.route("/profiles")
def profiles():
    users = Use.query.all()

    return render_template('profiles.html', users=users)


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))


###
# The functions below should be applicable to all Flask apps.
###


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")