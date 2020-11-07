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
