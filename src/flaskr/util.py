import os
import logging
import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
import hashlib
import subprocess
from .db import *
from . import UPLOAD_FOLDER
from werkzeug.exceptions import abort
from playhouse.shortcuts import model_to_dict


def generate_validate_picture(num_chars = 5):
    candidate_char_set = string.digits + string.ascii_letters
    width, heighth = num_chars * 30, 40    # size of picture 130 x 50

    # generate an image object and set the fonts
    im = Image.new('RGB',(width, heighth), 'White')
    # font = ImageFont.truetype("arial.ttf", 28, encoding="unic")
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

def generate_filecont_hash(content):
    m = hashlib.sha256()
    m.update(content)
    return m.hexdigest()

def check_filecontent_hash(filehash, content):
    content_hash = generate_filecont_hash(content)
    return filehash == content_hash

# # search a keyword ST in titles
# def title_search(ST):
#     s = "%" + ST + "%"
#     t_posts = PostDB.select().where(PostDB.title ** s).order_by(PostDB.id.desc())
#     posts = []
#     for apost in t_posts:
#         ta = model_to_dict(apost)
#         this_user = model_to_dict(UserDB.select(UserDB.username).where(UserDB.id == ta['author']['id']).get())
#         ta['username'] = this_user['username']
#         posts.append(ta)

#     return posts


# TODO: for this family of functions, we can use some design patterns like strategy to simply it.
# # get a post to view by id
# def get_view_post(id, check_author=False):
#     try:
#         return_post = model_to_dict(
#             PostDB.select(PostDB.id, PostDB.title, PostDB.body, PostDB.created, PostDB.author_id,
#                         PostDB.num_view, PostDB.num_reply).where(PostDB.id == id).get())
#     except PostDB.DoesNotExist:
#         abort(404, "Post id {0} doesn't exist.".format(id))

#     if check_author and return_post['author']['id'] != g.user['id']:
#         abort(403)

#     return_post['username'] = model_to_dict(UserDB.select(UserDB.username).where(UserDB.id == return_post['author']['id']).get())['username']

#     # pprint(return_post)

#     Files = PostFileDB.select().where(PostFileDB.post_id == id)
#     return_files = []
#     for File in Files:
#         return_files.append(model_to_dict(File))

#     replys = ReplyDB.select(ReplyDB.id, ReplyDB.author_id, ReplyDB.body, ReplyDB.created).where(ReplyDB.post_id == return_post['id'])
#     return_replys = []
#     for areply in replys:
#         dct_reply = model_to_dict(areply)
#         dct_reply['username'] = model_to_dict(UserDB.select(UserDB.username).where(UserDB.id == dct_reply['author']['id']).get())['username']
#         return_replys.append(dct_reply)

#     return_post['file'] = return_files
#     return_post['reply'] = return_replys

#     return return_post


# # delete the reply return the post id of it
# def delete_reply(id):
#     print("delete reply id = ", id)

#     post_id = model_to_dict(ReplyDB.select(ReplyDB.post_id).where(ReplyDB.id == id).get())['post_id']

#     print("post_id = ", post_id)

#     t = ReplyDB.delete().where(ReplyDB.id == id)
#     t.execute()

#     # update the the number of reply
#     apost = model_to_dict(PostDB.select(PostDB.num_reply).where(PostDB.id == post_id).get())
#     num_reply = int(apost['num_reply']) - 1

#     t = PostDB.update(num_reply=num_reply).where(PostDB.id == post_id)
#     t.execute()
#     print("num_reply", num_reply)

#     return post_id


# # delete a post by id
# def delete_post(id):
#     savepath = current_app.config['UPLOAD_FOLDER']

#     file_list = []
#     file_lists = PostFileDB.select(PostFileDB.filename, PostFileDB.id).where(PostFileDB.post_id == id)
#     for afile in file_lists:
#         file_list.append(model_to_dict(afile))

#     print("filelist = \n", file_list)

#     t = PostFileDB.delete().where(PostFileDB.post_id == id)
#     t.execute()

#     print("delete files from MySQL")
#     for file in file_list:
#         filename = str(file['id']) + "_" + file["filename"]
#         filename = os.path.join(savepath, filename)
#         print(filename)
#         process = subprocess.Popen(["del", filename], shell=True)
#         print("%s deleted" % (filename))

#     t = ReplyDB.delete().where(ReplyDB.post_id == id)
#     t.execute()

#     t = PostDB.delete().where(PostDB.id == id)
#     t.execute()

# # search a keyword ST in users
# def user_search(ST):
#     s = "%" + ST + "%"

#     t_users = UserDB.select(UserDB.id, UserDB.username).where(UserDB.username ** s)

#     users = []
#     for auser in t_users:
#         users.append(model_to_dict(auser))

#     return users

# def SAVE_FILES(file_list, savepath, post_id):
#     logging.info(f"file list len for post {post_id}: {len(file_list)}")
#     for file in file_list:
#         if not file.filename:
#             continue
#         file_content = file.read()
#         logging.info(f"{file.filename, file_content}")
#         filename = secure_filename(file.filename)

#         filehash = generate_filecont_hash(file_content)

#         t = PostFileDB.insert(filename=filename, filehash=filehash, post_id=post_id, created=datetime.datetime.now())
#         post_file_id = t.execute()

#         file_path = os.path.join(savepath, str(post_file_id) + "_" + filename)
#         with open(file_path, "wb") as fw:
#             fw.write(file_content)
#         print("Save %s to %s" % (filename, file_path))

