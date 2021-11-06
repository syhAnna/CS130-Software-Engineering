from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app,send_from_directory
)
import json
from .db import *
import datetime
from .util import *

from .auth import login_required

from pprint import pprint

from playhouse.shortcuts import model_to_dict


bp = Blueprint('blog', __name__)

# index page
@bp.route('/',methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        ST = request.form.get("searchkeywords",type=str,default=None)
        posts = title_search(ST)
        return redirect(url_for('blog.SEARCH_TITLE', ST=ST))

    posts, hots = get_index_info()
    session['hots'] = hots

    return render_template('blog/temp_index.html', posts=posts, hots=hots)


# create a new post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        savepath = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(savepath):
            os.mkdir(savepath)

        if not title:
            error = 'Title Is Required.'

        if error is not None:
            flash(error)
        else:
            t = PostDB.insert(title=title, body=body, author_id=g.user['id'], is_top=0, is_fine=0, created=datetime.datetime.now())
            post_id = t.execute()
            print(post_id)

            SAVE_FILES(request.files.getlist("file"), savepath, post_id)
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_create.html')


# view a post
@bp.route('/ViewPost/<int:id>', methods=('GET', 'POST'))
def ViewPost(id):
    if request.method == 'POST':
        body = request.form.get("body",type=str,default=None)
        ST = request.form.get("searchkeywords",type=str,default=None)
        Filename = request.form.get("file",type=str,default=None)
        if body:
            error = None
        if ST:
            posts = title_search(ST)
            return redirect(url_for('blog.SEARCH_TITLE', ST=ST))
            return render_template('blog/temp_SearchResult.html', posts=posts)
            error = None

        if error is not None:
            flash(error)
        else:
            t = ReplyDB.insert(body=body, author_id=g.user['id'], post_id=id, created=datetime.datetime.now())
            t.execute()

            print("insert done!")

            apost = get_view_post(id)

            # update the the number of reply
            num_reply = int(apost['num_reply']) + 1

            t = PostDB.update(num_reply=num_reply).where(PostDB.id == id)
            t.execute()
            print("num_reply", num_reply)

    apost = get_view_post(id)
    pprint(apost)

    # update the the number of views
    num_view = int(apost['num_view']) + 1

    t = PostDB.update(num_view=num_view).where(PostDB.id==id)
    t.execute()
    is_like = None
    is_collect = None
    if g.user:
        is_like = check_is_like(g.user['id'], id)
        is_collect = check_is_collect(g.user['id'], id)
        print("is_like = ", is_like)
        print("is_collect = ", is_collect)

    return render_template('blog/temp_ViewPost.html', post=apost, is_collect=is_collect, is_like=is_like, hots=session['hots'])


def CHECK_DOWNLOADFILE(post_file_id, filename):
    with open(filename, "rb") as f:
        content = f.read()
        filehash = model_to_dict(PostFileDB.select().where(PostFileDB.id == post_file_id).get())['filehash']
        if not check_filecontent_hash(filehash, content):
            error = "File Has Been Modified"
            return error


@bp.route('/DownloadFile/<string:filename>', methods=('POST', ))
def DownloadFile(filename):
    print(filename)
    tmp_list = eval(filename)
    filename = tmp_list[0]
    post_file_id = tmp_list[1]
    post_id = tmp_list[2]
    filename = str(post_file_id)+"_"+filename
    error = CHECK_DOWNLOADFILE(post_file_id, os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    if error:
        flash(error)
        return redirect(url_for("blog.ViewPost", id=post_id))

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# delete a reply by id
@bp.route('/DeleteReply/<int:id>', methods=('POST',))
@login_required
def DeleteReply(id):
    post_id = delete_reply(id)

    return redirect(url_for('blog.ViewPost', id=post_id))


@bp.route('/DeletePost/<int:id>', methods=('POST',))
@login_required
def DeletePost(id):
    delete_post(id)

    return redirect(url_for('blog.index'))


# search a keyword ST in titles
@bp.route('/SEARCH/TITLE/<string:ST>', methods=('GET','POST'))
@login_required
def SEARCH_TITLE(ST):
    if request.method == 'POST':
        ST = request.form.get("searchkeywords", type=str,default=None)
        # posts = title_search(ST)
        return redirect(url_for('blog.SEARCH_TITLE', ST=ST))
    posts = title_search(ST)
    users = user_search(ST)
    return render_template('blog/temp_SearchResult.html', posts=posts, users=users)


# search a keyword ST in users
@bp.route('/SEARCH/USER/<string:ST>')
@login_required
def SEARCH_USER(ST):
    users = user_search(ST)

    return json.dumps(users, ensure_ascii=False)


# like a post
@bp.route('/LIKE/<int:id>', methods=('GET', 'POST'))
@login_required
def LIKE(id):
    ADD_LIKE(id)

    return redirect(url_for('blog.ViewPost', id=id))


# collect a post
@bp.route('/COLLECT/<int:id>', methods=('GET', 'POST'))
@login_required
def COLLECT(id):
    ADD_COLLECT(id)

    return redirect(url_for('blog.ViewPost', id=id))


# collect a post
@bp.route('/UNCOLLECT/<int:id>', methods=('GET', 'POST'))
@login_required
def UNCOLLECT(id):
    ADD_UNCOLLECT(id)

    return redirect(url_for('blog.ViewPost', id=id))


# unlike a post
@bp.route('/UNLIKE/<int:id>', methods=('GET', 'POST'))
@login_required
def UNLIKE(id):
    ADD_UNLIKE(id)

    return redirect(url_for('blog.ViewPost', id=id))


''' # update a post
@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            conn, db = get_db()
            db.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )
            conn.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/temp_update.html', post=post) '''
