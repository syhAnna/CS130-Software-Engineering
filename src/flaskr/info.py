import os
import logging
from .db import *
from .util import *
from werkzeug.utils import secure_filename
from playhouse.shortcuts import model_to_dict
from werkzeug.security import check_password_hash

class ImageInfo:
    @staticmethod
    def get_image_by_id(image_id):
        image = model_to_dict(ImageDB.select(ImageDB.filename, ImageDB.filehash).where(ImageDB.id == image_id).get())
        return image
    
    @staticmethod
    def add_new_image(file, savepath):
        file_content = file.read()
        logging.info(f"add_new_image {file.filename}")
        filename = secure_filename(file.filename)
        filehash = generate_filecont_hash(file_content)

        image_id = ImageDB.insert({
            ImageDB.filename: filename, 
            ImageDB.filehash: filehash
        }).execute()

        file_path = os.path.join(savepath, str(image_id) + "_" + filename)
        with open(file_path, "wb") as fw:
            fw.write(file_content)
        logging.info("Save %s to %s" % (filename, file_path))
        return image_id
    
    @staticmethod
    def delete_image(image_id):
        ImageDB.delete().where(ImageDB.id == image_id)

class UserInfo:
    def __init__(self, uid=-1, uname="", pets = [],
                 image=None, email=None, register_date=None):
        self.uid = uid
        self.email = email
        self.uname = uname
        self.register_date = register_date
        self.pets = pets
        self.uimage = image
    
    """
    Add a new user with the given information to the database

    parameters:
        username (string): the new user's username
        password (string): the new user's password
        email (string): the new user's email
    return:
        uid (int): the new user's unique id
    """
    @staticmethod
    def add_new_user(username, password, email):
        uid = UserDB.insert({
            UserDB.username: username,
            UserDB.password: password,
            UserDB.email: email,
            UserDB.created: datetime.datetime.now(),
            UserDB.image_id: 2
        }).execute()
        return uid
    
    """
    Get user information stored in database with the given form that contains username, password and the verification code if the verification code and password matches. Otherwise, return null user information and error message.

    parameters:
        form (dictionary): contains username, password, imagecode
        correct_imagecode (string): this will be used to compared with the imagecode in the form
    
    return:
        user_info (dictionary / None): the user information stored in database, if doesn't exist or match failure, return none.
        error (string / None): if error occur, return error message, otherwise return None
    """
    @staticmethod
    def get_login_info(form, correct_imagecode):
        username = form['username']
        password = form['password']
        imagecode = form['imagecode']
        error = None
        user_info = UserDB.select().where(UserDB.username == username)
        if len(user_info) == 0:
            error = "Error: Username Does Not Exist"
            user_info = None
        else:
            user_info = user_info.get()
            logging.info(f"input password {password}, password in db {user_info.__dict__}")
            if not check_password_hash(user_info.password, password):
                error = "Error: Password Incorrect"
            elif imagecode != correct_imagecode:
                error = "Error: Imagecode Incorrect"
        return user_info, error

    """
    Get user information of given user id

    parameter:
    uid (int): user's unique id
    
    return:
    user_info (dictionary): all the user's information (including the pets information)
    """
    @staticmethod
    def get_user_info_by_uid(uid):
        uinfo = model_to_dict(UserDB.select(UserDB.id, UserDB.username, UserDB.email, UserDB.created).where(UserDB.id == uid).get())
        logging.info(f"get user info {uinfo}")
        pets = PetInfo.get_pets_by_uid(uid)
        # image = ImageInfo.get_image_by_id(image_id=uinfo["image"]["id"])
        uinfo["pets"] = pets
        return uinfo 
        # return UserInfo(uid=uid, uname=uinfo["username"], email=uinfo["email"],
        #                 register_date=uinfo["created"], pets=pets, image=image)

class PetInfo:
    def __init__(self, pid=-1, plocation="",
                    pweight=-1, p_age=-1, ptype = "",
                    pdescription="", pimage = None):
        self.pid = pid
        self.p_age = p_age
        self.ptype = ptype
        self.pweight = pweight
        self.pimage = pimage
        self.plocation = plocation
        self.pdescription = pdescription
        # self.pgender = pgender
    
    """
    Add a new pet with the given information to the database

    parameters:
        form (dictionary): the information about the pet, contains owner id, age, weight, type, city, description
        file: the image of the pet
    
    return:
        pet_id (int): the unique pet id.
    """
    @staticmethod
    def add_new_pet(form, file):
        image_id = 1
        if file is not None and file.filename:
            savepath = form["savepath"]
            if not os.path.exists(savepath):
                os.mkdir(savepath)
            image_id = ImageInfo.add_new_image(file, savepath)

        pet_id = PetDB.insert({
            PetDB.image_id: image_id,
            PetDB.owner_id: form["owner_id"],
            PetDB.age: form["age"],
            PetDB.weight: form["weight"],
            PetDB.type: form["type"],
            PetDB.location: form["city"],
            PetDB.description: form["description"]
        }).execute()
        return pet_id, ""

    """
    Get all the owned pet information of a given user id

    parameter:
        uid (int): user's unique id

    return:
        pets (list): a list of the user's pets information
    """
    @staticmethod
    def get_pets_by_uid(uid):
        pets = []
        raw_pets = PetDB.select(PetDB.id, PetDB.age, PetDB.weight, PetDB.type,
                                PetDB.created, PetDB.description, PetDB.image_id)\
                                .where(PetDB.owner_id == uid).order_by(PetDB.created.desc())
        for pet in raw_pets:
            # image = ImageInfo.get_image_by_id(image_id=pet["image"]["id"])
            pets.append(pet)
            # pets.append(PetInfo(pid=pet["id"], pweight=pet["weight"], p_age=pet["age"], 
            #                     ptype=pet["type"], pdescription=pet["description"], pimage=image))
        return pets   

    """
    Get all the pets information

    parameters: None

    return: 
        pets (list): a list of all the pets information
    """
    @staticmethod
    def get_pets():
        allpets = PetDB.select()
        allpets = sorted(allpets, key=lambda p: p.created, reverse=True)
        pets = []
        for pet in allpets:
            pet = model_to_dict(pet)
            pets.append(pet)
        logging.info(f"posts: {pets}")
        # for i, apost in enumerate(posts):
        #     tmp_files = []
        #     allfiles = PostFileDB.select().where(PostFileDB.post_id == apost['id'])
        #     for afile in allfiles:
        #         tmp_files.append(model_to_dict(afile))
        #     posts[i]['files'] = tmp_files
        return pets


    """
    Get the pet information given a unique pet id
    
    parameter:
        pet_id (int): the unique pet id

    return:
        pet (dictionary): all the information related to the pet.
    """
    @staticmethod
    def get_pet_for_view(pet_id):
        pet = model_to_dict(PetDB.select().where(PetDB.id == pet_id).get())
        pet["username"] = pet["owner"]["username"] # TODO: modify username to owner_name
        pet.pop("owner")
        pet["image"] = pet["image"]["filename"]
        pet["reply"] = ReplyInfo.get_reply_by_pid(pet_id)
        return pet
    
    """
    Delete a certain pet's information in the database

    parameter:
        pet_id (int): the unique pet id
    
    return: None
    """
    @staticmethod
    def delete_pet(pet_id):
        image_id = PetDB.select(PetDB.image_id).where(PetDB.id == pet_id).get()
        ImageInfo.delete_image(image_id)
        ReplyInfo.delete_reply_by_pet_id(pet_id)
        PetDB.delete().where(PetDB.id == pet_id).execute()

class ReplyInfo:
    @staticmethod
    def get_reply_by_pid(pet_id):
        allreplys = ReplyDB.select().where(ReplyDB.pet_id == pet_id)
        replys = []
        for reply in allreplys:
            reply = model_to_dict(reply)
            reply['username'] = reply["author"]["username"]
            reply.pop("author")
            reply.pop("pet")
            replys.append(reply)
        return replys
    
    @staticmethod
    def add_reply(form, pet_id):
        reply_id = ReplyDB.insert(body=form["body"], author_id=form['author_id'], pet_id=pet_id).execute()
        return reply_id
    
    @staticmethod
    def delete_reply(reply_id):
        ReplyDB.delete().where(ReplyDB.id == reply_id).execute()
    
    @staticmethod
    def delete_reply_by_pet_id(pet_id):
        ReplyDB.delete().where(ReplyDB.pet_id == pet_id).execute()
    

