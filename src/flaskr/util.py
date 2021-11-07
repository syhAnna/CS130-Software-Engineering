import os
import logging
import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
import hashlib
import subprocess
from .db import *
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from playhouse.shortcuts import model_to_dict


def generate_validate_picture(num_chars = 5):
    candidate_char_set = string.digits + string.ascii_letters
    width, heighth = num_chars * 30, 40    # size of picture 130 x 50

    # generate an image object and set the fonts
    im = Image.new('RGB',(width, heighth), 'White')
    font = ImageFont.truetype("/Library/Fonts/Arial", 28)
    draw = ImageDraw.Draw(im)
    generated_string = ''
    # output each char
    for item in range(num_chars):
        text = random.choice(candidate_char_set)
        generated_string += text
        draw.text((13 + random.randint(4, 7) + 20*item, random.randint(3, 7)), text=text, fill='Black', font=font)

    # draw several lines
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, heighth/2)
        x2 = random.randint(0, width)
        y2 = random.randint(heighth/2, heighth)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

    # Vague
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, generated_string


# TODO: for this family of functions, we can use some design patterns like strategy to simply it.
# check if the post is collected by user
def check_is_collect(user_id, post_id):
    try:
        t = CollectsDB.select().where(CollectsDB.author_id == user_id, CollectsDB.post_id == post_id).get()
        return True
    except CollectsDB.DoesNotExist:
        return False


# check if the post is collected by user
def check_is_like(user_id, post_id):
    try:
        t = LikesDB.select().where(LikesDB.author_id == user_id, LikesDB.post_id == post_id).get()
        return True
    except LikesDB.DoesNotExist:
        return False


# get num_like from a post
def get_like(post_id):
    num_like = model_to_dict(PostDB.select(PostDB.num_like).where(PostDB.id == post_id).get())['num_like']

    return num_like


# get num_collect from a post
def get_collect(post_id):
    num_collect = model_to_dict(PostDB.select(PostDB.num_collect).where(PostDB.id == post_id).get())['num_collect']

    return num_collect


 # get a specific post by id
def get_post(id, check_author=True):
    try:
        apost = model_to_dict(PostDB.select(PostDB.id, PostDB.title, PostDB.body, PostDB.created, PostDB.author_id, PostDB.is_top, PostDB.is_fine).where(PostDB.id == id).get())
    except PostDB.DoesNotExist:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and apost['author']['id'] != g.user['id']:
        abort(403)

    return apost


# get a post to view by id
def get_view_post(id, check_author=False):
    try:
        return_post = model_to_dict(
            PostDB.select(PostDB.id, PostDB.title, PostDB.body, PostDB.created, PostDB.author_id, PostDB.is_top, PostDB.is_fine,
                        PostDB.num_view, PostDB.num_reply, PostDB.num_like, PostDB.num_collect).where(PostDB.id == id).get())
    except PostDB.DoesNotExist:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and return_post['author']['id'] != g.user['id']:
        abort(403)

    return_post['username'] = model_to_dict(UserDB.select(UserDB.username).where(UserDB.id == return_post['author']['id']).get())['username']

    # pprint(return_post)

    Files = PostFileDB.select().where(PostFileDB.post_id == id)
    return_files = []
    for File in Files:
        return_files.append(model_to_dict(File))

    replys = ReplyDB.select(ReplyDB.id, ReplyDB.author_id, ReplyDB.body, ReplyDB.created).where(ReplyDB.post_id == return_post['id'])
    return_replys = []
    for areply in replys:
        dct_reply = model_to_dict(areply)
        dct_reply['username'] = model_to_dict(UserDB.select(UserDB.username).where(UserDB.id == dct_reply['author']['id']).get())['username']
        return_replys.append(dct_reply)

    return_post['file'] = return_files
    return_post['reply'] = return_replys

    return return_post


# delete the reply return the post id of it
def delete_reply(id):
    print("delete reply id = ", id)

    post_id = model_to_dict(ReplyDB.select(ReplyDB.post_id).where(ReplyDB.id == id).get())['post_id']

    print("post_id = ", post_id)

    t = ReplyDB.delete().where(ReplyDB.id == id)
    t.execute()

    # update the the number of reply
    apost = model_to_dict(PostDB.select(PostDB.num_reply).where(PostDB.id == post_id).get())
    num_reply = int(apost['num_reply']) - 1

    t = PostDB.update(num_reply=num_reply).where(PostDB.id == post_id)
    t.execute()
    print("num_reply", num_reply)

    return post_id


# delete a post by id
def delete_post(id):
    savepath = current_app.config['UPLOAD_FOLDER']

    file_list = []
    file_lists = PostFileDB.select(PostFileDB.filename, PostFileDB.id).where(PostFileDB.post_id == id)
    for afile in file_lists:
        file_list.append(model_to_dict(afile))

    print("filelist = \n", file_list)

    t = CollectsDB.delete().where(CollectsDB.post_id == id)
    t.execute()

    t = LikesDB.delete().where(LikesDB.post_id == id)
    t.execute()

    t = PostFileDB.delete().where(PostFileDB.post_id == id)
    t.execute()

    print("delete files from MySQL")
    for file in file_list:
        filename = str(file['id']) + "_" + file["filename"]
        filename = os.path.join(savepath, filename)
        print(filename)
        process = subprocess.Popen(["del", filename], shell=True)
        print("%s deleted" % (filename))

    t = ReplyDB.delete().where(ReplyDB.post_id == id)
    t.execute()

    t = PostDB.delete().where(PostDB.id == id)
    t.execute()


def get_index_info():
    posts = []
    allposts = PostDB.select()
    for apost in allposts:
        dct_apost = model_to_dict(apost)
        this_user = model_to_dict(UserDB.select(UserDB.nickname, UserDB.username).where(UserDB.id == dct_apost['author']['id']).get())
        dct_apost['username'] = this_user['username']
        dct_apost['nickname'] = this_user['nickname']

        posts.append(dct_apost)

    logging.info(f"posts: {posts}")
    posts = sorted(posts, key=lambda p: p['created'], reverse=True)

    for i, apost in enumerate(posts):
        tmp_files = []
        allfiles = PostFileDB.select().where(PostFileDB.post_id == apost['id'])
        for afile in allfiles:
            tmp_files.append(model_to_dict(afile))
        posts[i]['files'] = tmp_files

    hots = []
    allhots = PostDB.select().order_by(PostDB.hot.desc())
    for ahot in allhots:
        dcthot = model_to_dict(ahot)
        auser = model_to_dict(UserDB.select(UserDB.username, UserDB.nickname).where(UserDB.id == dcthot['author']['id']).get())
        dcthot['username'] = auser['username']
        dcthot['nickname'] = auser['nickname']
        hots.append(dcthot)

    return posts, hots


# search a keyword ST in titles
def title_search(ST):
    s = "%" + ST + "%"
    t_posts = PostDB.select().where(PostDB.title ** s).order_by(PostDB.id.desc())
    posts = []
    for apost in t_posts:
        ta = model_to_dict(apost)
        this_user = model_to_dict(UserDB.select(UserDB.nickname, UserDB.username).where(UserDB.id == ta['author']['id']).get())
        ta['username'] = this_user['username']
        ta['nickname'] = this_user['nickname']
        posts.append(ta)

    return posts


# search a keyword ST in users
def user_search(ST):
    s = "%" + ST + "%"

    t_users = UserDB.select(UserDB.id, UserDB.username, UserDB.nickname).where(UserDB.username ** s)

    users = []
    for auser in t_users:
        users.append(model_to_dict(auser))

    return users


def ADD_LIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == False):
        print("add like!")

        t = LikesDB.insert(author_id=user_id, post_id=id)
        t.execute()

        num_like = get_like(id) + 1

        t = PostDB.update(num_like=num_like).where(PostDB.id==id)
        t.execute()

        print("num_like = ", num_like)


def ADD_UNLIKE(id):
    user_id = g.user['id']
    print("user_id = ", user_id)

    is_like = check_is_like(user_id, id)
    if (is_like == True):
        print("add unlike!")

        t = LikesDB.delete().where(LikesDB.author_id == user_id, LikesDB.post_id == id)
        t.execute()

        num_like = get_like(id) - 1

        t = PostDB.update(num_like=num_like).where(PostDB.id==id)
        t.execute()

        print("num_like = ", num_like)


def ADD_COLLECT(id):
    user_id = g.user['id']
    print("in collect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == False):
        print("Add Collect!")

        t = CollectsDB.insert(author_id=user_id, post_id=id)
        t.execute()

        num_collect = get_collect(id) + 1

        t = PostDB.update(num_collect=num_collect).where(PostDB.id==id)
        t.execute()

        print("num_collect = ", num_collect)


def ADD_UNCOLLECT(id):
    user_id = g.user['id']
    print("in uncollect user_id = ", user_id)

    is_collect = check_is_collect(user_id, id)
    if (is_collect == True):
        print("add uncollect!")

        t = CollectsDB.delete().where(CollectsDB.author_id == user_id, CollectsDB.post_id == id)
        t.execute()

        num_collect = get_collect(id) - 1

        t = PostDB.update(num_collect=num_collect).where(PostDB.id==id)
        t.execute()

        print("num_collect = ", num_collect)

def generate_filecont_hash(content):
    return hashlib.sha256().update(content).hexdigest()

def check_filecontent_hash(filehash, content):
    content_hash = generate_filecont_hash(content)
    return filehash == content_hash

def SAVE_FILES(file_list, savepath, post_id):
    logging.info(f"file list len for post {post_id}: {len(file_list)}")
    for file in file_list:
        if not file.filename:
            continue
        file_content = file.read()
        logging.info(f"{file.filename, file_content}")
        filename = secure_filename(file.filename)

        filehash = generate_filecont_hash(file_content)

        t = PostFileDB.insert(filename=filename, filehash=filehash, post_id=post_id, created=datetime.datetime.now())
        post_file_id = t.execute()

        file_path = os.path.join(savepath, str(post_file_id) + "_" + filename)
        with open(file_path, "wb") as fw:
            fw.write(file_content)
        print("Save %s to %s" % (filename, file_path))


# deprecated