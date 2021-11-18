# user_profile page
# show & set user profile
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
import logging

from .auth import login_required
from pprint import pprint
from .db import *
from .info import *
from playhouse.shortcuts import model_to_dict

bp = Blueprint('user', __name__, url_prefix='/user')

""" get user_info """
@bp.route('/home/<string:user_id>')
def home(user_id):
    user_info = UserInfo.get_user_info_by_uid(user_id)
    logging.info(f"user info for {user_id}: {user_info}")
    return render_template('user/home.html', user=user_info)


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

    return render_template('user/easy_set.html')


@bp.route('/set', methods=('GET', 'POST'))
def set():
    
    if request.method == 'POST':
        if 'email' in request.form:
            email = request.form['email']
            t = UserDB.update(email=email).where(UserDB.id == g.user['id'])
            t.execute()
            return redirect(url_for('blog.index'))
        elif 'password' in request.form:
            nowpass = request.form['nowpass']
            password = request.form['password']
            repassword = request.form['repassword']
            real_password = model_to_dict(UserDB.select(UserDB.password).where(UserDB.id == g.user['id']).get())['password']
            error = None
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
        else:
            savepath = current_app.config['UPLOAD_FOLDER']
            file = request.files.get("photo", default=None)
            if file is not None and file.filename:
                if not os.path.exists(savepath):
                    os.mkdir(savepath)
                image_id = ImageInfo.add_new_image(file, savepath)
            t = UserDB.update(image_id=image_id).where(UserDB.id == g.user['id'])
            t.execute()
            return redirect(url_for('blog.index'))

    return render_template('user/easy_set.html')


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

    return render_template('user/easy_set.html')


# [TODO]: set user picture for user
@bp.route('/setpic', methods=('GET', 'POST'))
def setpic():
    if request.method == 'POST':
        pass

    return render_template('user/easy_set.html')

