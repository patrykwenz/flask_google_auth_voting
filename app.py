# Python standard libraries
import json
import os
import pymongo
import string
import random

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template, flash
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from profile_user import User
from vote import Vote
from table_config import *

GOOGLE_CLIENT_ID = "533144812198-9l5aidnhqlrmit1fr71pgg8bi4ek1ovv.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "-v18ectzMnQEASKErYMmfbaN"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"

)

client = pymongo.MongoClient(
    "mongodb+srv://patmis:konto123@cluster0.zfgls.mongodb.net/Test?retryWrites=true&w=majority")
db = client["Glosowanie"]

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def id_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(db, user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == "POST":
                other_questions = db["Info"].find()
                q = request.form["question"]

                if q == "":
                    flash("Question can not be empty", category="danger")
                    return render_template("admin2.html")

                for quer in other_questions:
                    if "".join(q.split(" ")).lower() == "".join(quer["title"].split(" ")).lower():
                        flash("Similar question already exists", category="danger")
                        return render_template("admin2.html")

                ans = []
                for a in request.form.getlist('answer'):
                    if a != "":
                        ans.append(a.strip())
                if len(ans) < 2:
                    flash("U need more answers", category="danger")
                    return render_template("admin2.html")

                if len(ans) > 20:
                    flash("Too many answers max is 20", category="danger")
                    return render_template("admin2.html")

                else:
                    ans_dict = {}
                    for key in ans:
                        ans_dict[key] = "".join(key.split(" ")).lower()
                    voting_id = id_generator()
                    query = {
                        "voting_id": voting_id,
                        "title": q,
                        "ans": ans_dict,
                        "creator": current_user.id

                    }
                    cluster_insert = db["Info"].insert_one(query)
                    flash("Question added", category="info")
                    return render_template("admin2.html")
            return render_template("admin2.html")

        else:
            flash("You are not an admin", category="danger")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))


@app.route("/admin/delete", methods=["GET", "POST"])
def admin_delete():
    if current_user.is_authenticated:
        if current_user.is_admin:
            vote_labels = []
            query = db["Info"].find()
            for col in query:
                vote_labels.append([col["voting_id"], col["title"]])
            if request.method == "POST":
                query = db["Info"].delete_one({"voting_id": request.form["voting_id"]})
                flash('Succesfully deleted', category="info")
                return redirect(url_for("admin_delete"))
            return render_template("admin_delete.html", vote_labels=vote_labels)
        else:
            flash("You are not an admin", category="danger")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/vote")
def vote():
    vote_labels = list(db["Info"].distinct("voting_id"))
    return redirect(url_for("voteparam", voting_id=vote_labels[0]))


@app.route("/vote/<voting_id>", methods=["GET", "POST"])
def voteparam(voting_id):
    vote_labels = []
    query = db["Info"].find()
    for col in query:
        vote_labels.append([col["voting_id"], col["title"]])

    voting_data = db["Info"].find_one({"voting_id": voting_id})
    q = voting_data["title"]
    answers_ids = voting_data["ans"].values()
    print(answers_ids)

    if current_user.is_authenticated:
        if request.method == "POST":
            checboxes_votes = [val for val in request.form]
            print(request.data)
            print(checboxes_votes)

            if len(checboxes_votes) == 0:
                flash('Vote can not be empty', category="danger")
                return render_template("vote.html", question=q, answers=answers_ids, vote_labels=vote_labels)

            if len(checboxes_votes) > 1:
                flash('Too many args', category="danger")
                return render_template("vote.html", question=q, answers=answers_ids, vote_labels=vote_labels)

            else:
                voters_id = current_user.id
                if Vote.vote_exists(db, voters_id, voting_id):
                    flash('You can not vote more than once', category="danger")
                    return render_template("vote.html", question=q, answers=answers_ids, vote_labels=vote_labels)
                else:
                    vote_id = str(checboxes_votes[0])
                    swapped = {value: key for key, value in voting_data["ans"].items()}
                    vote = swapped[vote_id]
                    Vote.create(db, voters_id, vote, voting_id)
                    return redirect(url_for("resultsparam", voting_id=voting_id))
    else:
        return redirect(url_for("login"))

    return render_template("vote.html", question=q, answers=answers_ids, vote_labels=vote_labels)


@app.route("/results")
def results():
    vote_labels = list(db["Info"].distinct("voting_id"))
    return redirect(url_for("resultsparam", voting_id=vote_labels[0]))


@app.route("/results/<voting_id>")
def resultsparam(voting_id):
    vote_labels = []
    query = db["Info"].find()
    for col in query:
        vote_labels.append([col["voting_id"], col["title"]])

    # get vote info
    voting_data = db["Info"].find_one({"voting_id": voting_id})
    title = voting_data["title"]
    bar_labels = voting_data["ans"].keys()
    print("lab", bar_labels)

    bar_values = []
    for field in bar_labels:
        count = db[voting_id].count_documents({"vote": field})
        print(field, count)
        bar_values.append(count)

    background_colors = possible_background_colors[:len(bar_labels)]
    border_colors = possible_border_colors[:len(bar_labels)]
    return render_template("results2.html", title=title,
                           labels=bar_labels, values=bar_values, colors=background_colors, borders=border_colors,
                           vote_labels=vote_labels)


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture, is_admin=False
    )

    # Doesn't exist? Add it to the database.
    if not User.get(db, unique_id):
        User.create(db, unique_id, users_name, users_email, picture, False)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("vote"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context="adhoc", debug=True)
