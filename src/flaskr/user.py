# user_profile page
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from .auth import login_required
from pprint import pprint
from .db import *
from playhouse.shortcuts import model_to_dict

bp = Blueprint('user', __name__, url_prefix='/user')


def get_home_info(id):
    tmp_list = model_to_dict(UserDB.select(UserDB.username, UserDB.email, UserDB.created).where(UserDB.id == id).get())

    posts = []
    allposts = PostDB.select(PostDB.id, PostDB.title, PostDB.created, PostDB.author_id).where(PostDB.author_id == id).order_by(PostDB.created.desc())
    for apost in allposts:
        posts.append(model_to_dict(apost))

    return_collects = []
    user_info = {
        'username': tmp_list['username'],
        'email': tmp_list['email'],
        'created': tmp_list['created'],
        'posts': posts
        }

    return user_info


""" get user_info """
@bp.route('/home/<string:user_id>')
def home(user_id):
    user_info = get_home_info(user_id)
    logging.info(f"user info for {user_id}: {user_info}")

    return render_template('user/temp_home.html', user=user_info)


""" processing user_info modification request 
TODO[yikai, yuhan]: using one function to deal with different requests
like setUserInfo(param), setPetInfo(param)
"""
@bp.route('/setemail', methods=('GET', 'POST'))
def setemail():
    if request.method == 'POST':
        email = request.form['email']
        error = None

        if not email:
            error = 'Email is required.'

        if error is not None:
            flash(error)
        else:
            t = UserDB.update(email=email).where(UserDB.id == g.user['id'])
            t.execute()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setemail.html')


@bp.route('/setpass', methods=('GET', 'POST'))
def setpass():
    if request.method == 'POST':
        nowpass = request.form['nowpass']
        password = request.form['password']
        repassword = request.form['repassword']
        error = None

        real_password = model_to_dict(UserDB.select(UserDB.password).where(UserDB.id == g.user['id']).get())['password']

        if not (check_password_hash(real_password, nowpass)):
            error = 'Wrong password!'

        if not password:
            error = 'Password is required.'
        elif not (password ==repassword):
            error = 'Two passwords are inconsistent.'
        elif not (password == repassword):
            error = 'you enter different passwords!'
        elif ((len(password) < 6) or (len(password) > 16)):
            error = 'The length of password should be between 6 and 16.'

        if error is not None:
            flash(error)
        else:
            t = UserDB.update(password=generate_password_hash(password)).where(UserDB.id == g.user['id'])
            t.execute()

            return redirect(url_for('blog.index'))

    return render_template('user/temp_setpass.html')
