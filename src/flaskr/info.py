class UserInfo:
    def __init__(self, uid=-1, uname="", ugender="", pets = [],
                 ulocation="", display_pic=None, email=None,
                 register_date=None, free_duration=None, busy_duration=None):
        self.uid = uid
        self.email = email
        self.uname = uname
        self.ugender = ugender
        self.ulocation = ulocation
        self.display_pic = display_pic
        self.register_date = register_date
        self.pets = pets
        self.free_duration = free_duration
        self.busy_duration = busy_duration
    
    @staticmethod
    def get_user_info_by_uid(uid):
        return UserInfo()

class PetInfo:
    def __init__(self, pid=-1, pname="", pgender="",
                    pweight=-1, p_age=-1, ptype = "",
                    pdescription="", pimages = []):
        self.pid = pid
        self.p_age = p_age
        self.ptype = ptype
        self.pname = pname
        self.pgender = pgender
        self.pweight = pweight
        self.pimages = pimages
        self.pdescription = pdescription
    
    @staticmethod
    def get_pets_by_uid(uid):
        return []

class PostInfo:
    def __init__(self):
        pass

class Duration:
    def __init__(self):
        pass
        
    

