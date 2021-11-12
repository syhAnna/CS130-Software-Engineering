# main page
# 1. show posts in the nearby location
# 2. show 
from logging import log
from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app
)
from .info import *
from .util import *
from .auth import login_required


bp = Blueprint('blog', __name__)

# index page
@bp.route('/',methods=('GET', 'POST'))
def index():
    form = {}
    if request.method == 'POST':
        form = request.form
    posts = PetInfo.get_pets(form=form)
    return render_template('blog/index.html', posts=posts)


# create a new post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        form = dict(request.form)
        form["savepath"] = current_app.config['UPLOAD_FOLDER']
        form["owner_id"] = g.user['id']
        file = request.files.get("photo", default=None)
        logging.info(f"request.form for create {form}, {request.files}")
        pet_id, error = PetInfo.add_new_pet(form, file=file)
        if not error:
            return redirect(url_for('blog.index'))
        flash(error)

    return render_template('blog/create.html')

@bp.route('/ViewPost/<int:pet_id>', methods=('GET', 'POST'))
def ViewPost(pet_id):
    if request.method == 'POST':
        form = dict(request.form)
        form["author_id"] = g.user['id']
        ReplyInfo.add_reply(form, pet_id)

    pet = PetInfo.get_pet_for_view(pet_id)
    logging.info(f"info of pet is {pet}")
    return render_template('blog/ViewPost.html', post=pet)


# delete a reply by id
@bp.route('/DeleteReply/<int:id>', methods=('POST',))
@login_required
def DeleteReply(id):
    post_id = ReplyInfo.delete_reply(id)
    return redirect(url_for('blog.ViewPost', id=post_id))


@bp.route('/DeletePost/<int:id>', methods=('POST',))
@login_required
def DeletePost(id):
    PetInfo.delete_pet(id)
    return redirect(url_for('blog.index'))

# def CHECK_DOWNLOADFILE(post_file_id, filename):
#     with open(filename, "rb") as f:
#         content = f.read()
#         filehash = model_to_dict(PostFileDB.select().where(PostFileDB.id == post_file_id).get())['filehash']
#         if not check_filecontent_hash(filehash, content):
#             error = "File Has Been Modified"
#             return error


# @bp.route('/DownloadFile/<string:filename>', methods=('POST', ))
# def DownloadFile(filename):
#     print(filename)
#     tmp_list = eval(filename)
#     filename = tmp_list[0]
#     post_file_id = tmp_list[1]
#     post_id = tmp_list[2]
#     filename = str(post_file_id)+"_"+filename
#     error = CHECK_DOWNLOADFILE(post_file_id, os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
#     if error:
#         flash(error)
#         return redirect(url_for("blog.ViewPost", id=post_id))

#     return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
