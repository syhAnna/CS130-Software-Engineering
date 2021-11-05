# -*- coding: utf-8 -*-
# author: zyk
# create a connection to it. Any queries and operations are performed using the connection


from flask import current_app, g
from flask.cli import with_appcontext
import json
from peewee import *

dbConfig = json.load(open("flaskr/dbConfig.json"))
host, user, passwd, database = dbConfig["host"], dbConfig["user"], dbConfig["passwd"], dbConfig["database"]
mydatabase = MySQLDatabase(host=host, user=user, passwd=passwd, database=database, charset="utf8", port=3306)
mydatabase.connect()


class BaseModel(Model):
    class Meta:
        database = mydatabase

class user(BaseModel):
    id = IntegerField(primary_key=True)
    created = DateTimeField()
    username = CharField(unique=True)
    nickname = CharField()
    password = CharField()
    email = CharField(default="")
    is_block = BooleanField(default=0)

class post(BaseModel):
    id = IntegerField(primary_key=True)
    post_author = ForeignKeyField(user, backref="user_id")
    author_id = IntegerField()
    num_view = IntegerField(default=0)
    num_reply = IntegerField(default=0)
    num_like = IntegerField(default=0)
    num_collect = IntegerField(default=0)
    hot = DoubleField(default=0.0)
    created = DateTimeField()
    title = TextField()
    body = TextField()
    is_top = BooleanField(default=0)
    is_fine = BooleanField(default=0)

class reply(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    author_id = IntegerField()
    post_id = IntegerField()
    created = DateTimeField()
    body = TextField()

class collects(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    author_id = IntegerField()
    post_id = IntegerField()

class likes(BaseModel):
    id = IntegerField(primary_key=True)
    author = ForeignKeyField(user, backref="author_id1", column_name="author_id")
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    author_id = IntegerField()
    post_id = IntegerField()

class post_file(BaseModel):
    id = IntegerField(primary_key=True)
    created = DateTimeField()
    post = ForeignKeyField(post, backref="post_id1", column_name="post_id")
    post_id = IntegerField()
    created = DateTimeField()
    filename = TextField()
    filehash = TextField()

mydatabase.create_tables([user, post])
def init_app(app):
    return
