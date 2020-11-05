class Vote():
    def __init__(self, user_id, vote):
        self.user_id = user_id
        self.vote = vote

    @staticmethod
    def vote_exists(db, user_id):
        collection = db["Votes"]
        if collection.find_one({"user_id": user_id}) is None:
            return False
        return True

    @staticmethod
    def create(db, user_id, vote):
        collection = db["Votes"]
        collection.insert_one({
            "user_id": user_id,
            "vote": vote,
        })
