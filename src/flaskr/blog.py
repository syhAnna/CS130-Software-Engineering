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

# TODO: search part
# index page
@bp.route('/',methods=('GET', 'POST'))
def index():
    # if request.method == 'POST':
    #     ST = request.form.get("searchkeywords",type=str,default=None)
    #     posts = title_search(ST)
    #     return redirect(url_for('blog.SEARCH_TITLE', ST=ST))

    posts = PetInfo.get_pets()
    return render_template('blog/index.html', posts=posts)


# create a new post
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        form = dict(request.form)
        form["savepath"] = current_app.config['UPLOAD_FOLDER']
        form["owner_id"] = g.user['id']
        file_list = request.files.getlist("file")
        file = None
        for tfile in file_list:
            if tfile.filename:
                file = tfile
        pet_id, error = PetInfo.add_new_pet(form, file=file)
        if not error:
            return redirect(url_for('blog.index'))
        flash(error)

        # if error is not None:
        #     flash(error)
        # else:
        #     t = PostDB.insert(title=title, body=body, author_id=g.user['id'], created=datetime.datetime.now())
        #     post_id = t.execute()
        #     print(post_id)

        #     SAVE_FILES(request.files.getlist("file"), savepath, post_id)
        #     return redirect(url_for('blog.index'))

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

# # view a post
# @bp.route('/ViewPost/<int:id>', methods=('GET', 'POST'))
# def ViewPost(id):
#     if request.method == 'POST':
#         body = request.form.get("body",type=str,default=None)
#         ST = request.form.get("searchkeywords",type=str,default=None)
#         Filename = request.form.get("file",type=str,default=None)
#         if body:
#             error = None
#         if ST:
#             posts = title_search(ST)
#             return redirect(url_for('blog.SEARCH_TITLE', ST=ST))
#             return render_template('blog/temp_SearchResult.html', posts=posts)
#             error = None

#         if error is not None:
#             flash(error)
#         else:
#             t = ReplyDB.insert(body=body, author_id=g.user['id'], post_id=id, created=datetime.datetime.now())
#             t.execute()

#             print("insert done!")

#             apost = get_view_post(id)

#             # update the the number of reply
#             num_reply = int(apost['num_reply']) + 1

#             t = PostDB.update(num_reply=num_reply).where(PostDB.id == id)
#             t.execute()
#             print("num_reply", num_reply)

#     apost = get_view_post(id)
#     pprint(apost)

#     # update the the number of views
#     num_view = int(apost['num_view']) + 1

#     t = PostDB.update(num_view=num_view).where(PostDB.id==id)
#     t.execute()

#     return render_template('blog/ViewPost.html', post=apost)


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


# # search a keyword ST in titles
# @bp.route('/SEARCH/TITLE/<string:ST>', methods=('GET','POST'))
# @login_required
# def SEARCH_TITLE(ST):
#     if request.method == 'POST':
#         ST = request.form.get("searchkeywords", type=str,default=None)
#         # posts = title_search(ST)
#         return redirect(url_for('blog.SEARCH_TITLE', ST=ST))
#     posts = title_search(ST)
#     # users = user_search(ST)
#     return render_template('blog/index.html', posts=posts)
#     # return render_template('blog/temp_SearchResult.html', posts=posts, users=users)


# # search a keyword ST in users
# @bp.route('/SEARCH/USER/<string:ST>')
# @login_required
# def SEARCH_USER(ST):
#     users = user_search(ST)

#     return json.dumps(users, ensure_ascii=False)
