from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_user, logout_user, \
    login_required, current_user

from project.models import *
from project import db, bcrypt, models
from .forms import LoginForm, RegisterForm, ChangePasswordForm

import importlib
import inspect


user_blueprint = Blueprint('user', __name__,)

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """This method represents route to the 'register.html' and serves as account registration feature.
    This method creates object of User class with data from register, adds this user to database and 
    subscribes user to all existing courses.

    Returns:
        render_template: Returns rendered 'register.html' template.
    """

    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username = form.username.data,
            password=form.password.data
        )

        # Add new user to all existing courses
        for name, obj in inspect.getmembers(models):
            if inspect.isclass(obj) and obj != User:
                registerCourse = obj(email=form.email.data)
                db.session.add(registerCourse)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('You registered and are now logged in. Welcome!', 'success')

        return redirect(url_for('main.home'))

    return render_template('user/register.html', form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """This method represents route to the 'login.html' and serves as login feature.
    This method validates user's credentials and if user exists and password is correct, then
    the user is logged into the application.

    Returns:
        render_template: Returns rendered 'login.html' template.
    """

    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(
            user.password, request.form['password']):
            login_user(user)
            flash('Welcome.', 'success')
            return redirect(url_for('main.home'))

        else:
            flash('Entered email and password did not match our records. \
                Please check your credentials and try again.', 'danger')
            return render_template('user/login.html', form=form)

    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    """This method serves as logout feature.

    Returns:
        redirect: Redirects to 'login.html' template.
    """

    logout_user()
    flash('You were logged out.', 'success')

    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """This method represents route to the 'profile.html'.
    The rendered template allows to change password.

    Returns:
        render_template: Returns rendered 'profile.html' template.
    """
    user = User.query.filter_by(email=current_user.email).first()
    registeredOn = user.get_registeredOn().strftime('%d %b %Y')

    form = ChangePasswordForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password successfully changed.', 'success')
            return redirect(url_for('user.profile'))

        else:
            flash('Password change was unsuccessful.', 'danger')
            return redirect(url_for('user.profile'))

    return render_template('user/profile.html', form=form, registeredOn=registeredOn)