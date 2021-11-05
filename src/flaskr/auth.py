# -*- coding: utf-8 -*-
# author: zyk
# A Blueprint is a way to organize a group of related views and other code.
# Rather than registering views and other code directly with an application,
# they are registered with a blueprint.


import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

from werkzeug.security import check_password_hash, generate_password_hash
from playhouse.shortcuts import model_to_dict
from .db import *
from .util import *
from io import BytesIO
import logging

bp = Blueprint('auth', __name__, url_prefix='/auth')

# TODO: now a window shows the error message, we want error message can show in the register page!
def get_register_info(form):
    username = form['username']
    password = form['password']
    nickname = form['nickname']
    repassword = form['repassword']
    email = form['email']
    imagecode = form['imagecode']
    error = None
    if not nickname:
        nickname = username
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
    elif len(nickname) > 40:
        error = 'The maximum size of nickname is 40, your username is too long!'
    elif len(user.select(user.id).where(user.username == username))>0 :
        error = 'User {} is already registered.'.format(username)
    elif imagecode != session['imagecode']:
        error = 'Imagecode incorrect'

    return username, generate_password_hash(password), nickname, email, error


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        logging.info(request.form)
        username, password, nickname, email, error = get_register_info(request.form)
        logging.info(f"new user info: username: {username}, nickname: {nickname}, error: {error}")

        if error is None:
            user.insert({
                user.username: username,
                user.password: password,
                user.nickname: nickname,
                user.email: email
            }).execute()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/temp_reg.html')


def get_login_info(form):
    username = form['username']
    password = form['password']
    imagecode = form['imagecode']
    error = None
    User = user.select().where(user.username == username)
    if len(User) == 0:
        error = "Username Does Not Exist"
        User = None
    else:
        User = User.get()
        if not check_password_hash(User.password, password):
            error = "Password Incorrect"
        elif imagecode != session['imagecode']:
            error = "Imagecode Incorrect"

    return User, error


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # logging.info(request.form)
        user, error = get_login_info(request.form)

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)    # stores messages that can be retrieved when rendering the template.

    return render_template('auth/temp_login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = model_to_dict(user.select().where(user.id == user_id).get())


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
