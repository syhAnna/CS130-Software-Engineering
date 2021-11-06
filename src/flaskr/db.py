# -*- coding: utf-8 -*-
# author: zyk
# create a connection to it. Any queries and operations are performed using the connection


from flask import current_app, g
from flask.cli import with_appcontext
import json
from peewee import *

dbConfig = json.load(open("flaskr/dbConfig.json"))
mydatabase = MySQLDatabase(host=dbConfig["host"],
                           user=dbConfig["user"],
                           passwd=dbConfig["passwd"],
                           database=dbConfig["database"],
                           charset="utf8",
                           port=3306)
mydatabase.connect()

# TODO[yinfan]: design database
class BaseModel(Model):
    class Meta:
        database = mydatabase

# peewee will generate an auto-increment field id for every db
class UserDB(BaseModel):
    created = DateTimeField()
    username = CharField(unique=True)
    nickname = CharField()
    password = CharField()
    email = CharField(default="")

    # discarded
    is_block = BooleanField(default=0)

class PostDB(BaseModel):
    author = ForeignKeyField(UserDB, backref="user_id")
    num_view = IntegerField(default=0)
    num_reply = IntegerField(default=0)
    created = DateTimeField()
    title = TextField()
    body = TextField()

    # discarded
    num_like = IntegerField(default=0)
    num_collect = IntegerField(default=0)
    hot = DoubleField(default=0.0)
    is_fine = BooleanField(default=0)
    is_top = BooleanField(default=0)


class ReplyDB(BaseModel):
    author = ForeignKeyField(UserDB, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(PostDB, backref="post_id1", column_name="post_id")
    created = DateTimeField()
    body = TextField()


class PostFileDB(BaseModel):
    post = ForeignKeyField(PostDB, backref="post_id1", column_name="post_id")
    created = DateTimeField()
    filename = TextField()
    filehash = TextField()

# discarded?
class CollectsDB(BaseModel):
    author = ForeignKeyField(UserDB, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(PostDB, backref="post_id1", column_name="post_id")

class LikesDB(BaseModel):
    author = ForeignKeyField(UserDB, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(PostDB, backref="post_id1", column_name="post_id")

mydatabase.create_tables([UserDB, PostDB, ReplyDB, PostFileDB, CollectsDB, LikesDB])
def init_app(app):
    return
