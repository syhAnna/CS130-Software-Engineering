# -*- coding: utf-8 -*-
# author: zyk
# responsible for login & logout & register


import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

from werkzeug.security import generate_password_hash
from .info import *
from .util import *
from .db import *
from io import BytesIO
import logging

# A Blueprint is a way to organize a group of related views and other code.
# Rather than registering views and other code directly with an application,
# they are registered with a blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')


# TODO: now a window shows the error message, we want error message can show in the register page!
def get_register_info(form):
    username = form['username']
    password = form['password']
    repassword = form['repassword']
    email = form['email']
    imagecode = form['imagecode']
    error = None
    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif not email:
        error = 'Email is required.'
    elif not repassword:
        error = 'Repassword is required'
    elif not (password == repassword):
        error = 'Two passwords are inconsistent.'
    elif ((len(password) < 6) or (len(password) > 16)):
        error = 'The length of password should be between 6 and 16.'
    elif len(username) > 40:
        error = 'The maximum size of username is 40, your username is too long!'
    elif len(UserDB.select(UserDB.id).where(UserDB.username == username))>0 :
        error = 'User {} is already registered.'.format(username)
    elif imagecode != session['imagecode']:
        error = 'Imagecode incorrect'

    return username, generate_password_hash(password), email, error


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username, password, email, error = get_register_info(request.form)
        logging.info(f"new user info: username: {username}, error: {error}")

        if error is None:
            UserInfo.add_new_user(username=username, password=password, email=email)
            return redirect(url_for('auth.login'))
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # logging.info(request.form)
        user_info, error = UserInfo.get_login_info(request.form, correct_imagecode=session['imagecode'])
        if error is None:
            session.clear()
            session['user_id'] = user_info.id
            return redirect(url_for('index'))
        flash(error)    # stores messages that can be retrieved when rendering the template.
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = UserInfo.get_user_info_by_uid(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            redirect(url_for('blog.index'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/code')
def get_code():
    # Write binary format image into the memory, release the space in disk
    image, str = generate_validate_picture()
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # send binary image as respond to the frontend and set the header
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # save image code as string into the session
    session['imagecode'] = str
    return response
