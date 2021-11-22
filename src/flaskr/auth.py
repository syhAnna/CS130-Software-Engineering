# -*- coding: utf-8 -*-
# author: zyk
# responsible for login & logout & register

import re
import functools
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

from werkzeug.security import generate_password_hash
from .info import *
from .util import *
from .db import *
from io import BytesIO
from .forms import RegistrationForm, LoginForm


# A Blueprint is a way to organize a group of related views and other code.
# Rather than registering views and other code directly with an application,
# they are registered with a blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')


# TODO: now a window shows the error message, we want error message can show in the register page!
# def get_register_info(form):
#     email_re = re.compile(r"[^@]+@[^@]+\.[^@]+")
#     password_format_re = re.compile(r" ^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$")
#     username = form['username']
#     password = form['password']
#     repassword = form['repassword']
#     email = form['email']
#     imagecode = form['imagecode']
#     if not username:
#         error = 'Username is required.'
#     elif not password:
#         error = 'Password is required.'
#     elif not email:
#         error = 'Email is required.'
#     elif not repassword:
#         error = 'Repassword is required'
#     elif not email_re.match(email):
#         error = 'The email address: {0} is not valid, please enter a valid address'.format(email)
#     elif not (password == repassword):
#         error = 'Two passwords are inconsistent.'
#     elif ((len(password) < 6) or (len(password) > 16)):
#         error = 'The length of password should be between 6 and 16.'
#     elif not password_format_re.match(password):
#         error = 'The password must contain numbers, capital and small letters'
#     elif len(username) > 40:
#         error = 'The maximum size of username is 40, your username is too long!'
#     elif len(UserDB.select(UserDB.id).where(UserDB.username == username))>0 :
#         error = 'User {} is already registered.'.format(username)
#     elif imagecode != session['imagecode']:
#         error = 'Imagecode incorrect'

#     return username, generate_password_hash(password), email, error


# Fan: modify the register() and login() function call with flask-wtf, now display all error messages at one time and
# and on the same page.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    forms = RegistrationForm()
    if request.method =='POST' and forms.validate():
        username = forms.username.data
        password = generate_password_hash(forms.password.data)
        email = forms.email.data
        imagecode = forms.imagecode.data
        print(password)
        code_error = None
        use_error = None
        if not session['imagecode'] == imagecode:
            code_error = 'Please enter the correct imagecode'
        if len(UserDB.select(UserDB.id).where(UserDB.username == username)) > 0:
            use_error = 'User {} is already registered.'.format(username)
        if code_error is not None and  use_error is not None:
            return render_template('auth/register.html', form=forms, use_error=use_error, code_error=code_error)
        elif code_error is not None:
            return render_template('auth/register.html', form=forms, code_error=code_error)
        elif use_error is not None:
            return render_template('auth/register.html', form=forms, use_error=use_error)
        else:
            UserInfo.add_new_user(username=username, password=password, email=email)
            return redirect(url_for('auth.login'))
        flash(f'Account created for {form.username.data}!', 'success')
    return render_template('auth/register.html', form=forms)

# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username, password, email, error = get_register_info(request.form)
#         logging.info(f"new user info: username: {username}, error: {error}")

#         if error is None:
#             UserInfo.add_new_user(username=username, password=password, email=email)
#             return redirect(url_for('auth.login'))
#         flash(error)
#     return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        # logging.info(request.form)
        username = form.username.data
        password = form.password.data
        imagecode = form.imagecode.data

        user_error = None
        pwd_error = None
        code_error = None
        user_info = UserDB.select().where(UserDB.username == username)
        if len(user_info) == 0:
            use_error = "Error: Username Does Not Exist"
            user_info = None
        else:
            user_info = user_info.get()
            logging.info(f"input password {password}, password in db {user_info.__dict__}")
            if not check_password_hash(user_info.password, password):
                pwd_error = "Error: Password Incorrect"
            elif imagecode != session['imagecode']:
                code_error = "Error: Imagecode Incorrect"

        if user_error is None and pwd_error is None and code_error is None:
            session.clear()
            session['user_id'] = user_info.id
            return redirect(url_for('index'))
        elif user_error is not None:
            return render_template('auth/login.html', form=form, user_error=user_error)
        elif pwd_error is not None:
            return render_template('auth/login.html', form=form, pwd_error=pwd_error)
        elif code_error is not None:
            return render_template('auth/login.html', form=form, code_error=code_error)
    return render_template('auth/login.html', form=form)


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
