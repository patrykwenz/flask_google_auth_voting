from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(db, user_id):
        collection = db["User"]
        user = collection.find_one({"_id": user_id})
        if not user:
            return None

        user = User(
            id_=user["_id"], name=user["name"], email=user["email"], profile_pic=user["profile_pic"]
        )
        return user

    @staticmethod
    def create(db, _id, name, email, profile_pic):
        collection = db["User"]
        collection.insert_one({
            "_id": _id,
            "name": name,
            "email": email,
            "profile_pic": profile_pic
        })