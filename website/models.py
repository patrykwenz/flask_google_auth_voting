from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, is_admin):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.is_admin = is_admin

    @staticmethod
    def get(db, user_id):
        collection = db["User"]
        user = collection.find_one({"_id": user_id})
        if not user:
            return None

        user = User(
            id_=user["_id"], name=user["name"], email=user["email"], profile_pic=user["profile_pic"],
            is_admin=user["is_admin"]
        )
        return user

    @staticmethod
    def create(db, _id, name, email, profile_pic, is_admin):
        collection = db["User"]
        collection.insert_one({
            "_id": _id,
            "name": name,
            "email": email,
            "profile_pic": profile_pic,
            "is_admin": is_admin
        })


class Vote():
    def __init__(self, user_id, vote):
        self.user_id = user_id
        self.vote = vote

    @staticmethod
    def vote_exists(db, user_id, voting_id):
        collection = db[voting_id]
        if collection.find_one({"user_id": user_id}) is None:
            return False
        return True

    @staticmethod
    def create(db, user_id, vote, voting_id):
        collection = db[voting_id]
        collection.insert_one({
            "user_id": user_id,
            "vote": vote,
        })
