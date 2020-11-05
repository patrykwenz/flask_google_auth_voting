# Python standard libraries
import json
import os
import pymongo

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


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(db, user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/vote", methods=["GET", "POST"])
def vote():
    q = "What is Your Favorite Colour?"
    colours = ["RED", "YELLOW", "BLUE"]
    if current_user.is_authenticated:
        if request.method == "POST":
            checboxes_votes = [val for val in request.form]
            print(checboxes_votes)
            if len(checboxes_votes) == 0:
                flash('Vote can not be empty', category="danger")
            if len(checboxes_votes) > 1:
                flash('Too many args', category="danger")
            else:
                voters_id = current_user.id
                if Vote.vote_exists(db, voters_id):
                    flash('You can not vote more than once', category="danger")
                    return render_template("vote.html", question=q, colours=colours)
                else:
                    vote = str(checboxes_votes[0])
                    Vote.create(db, voters_id, vote)
                    return redirect(url_for("results"))
    else:
        return redirect(url_for("login"))

    return render_template("vote.html", question=q, colours=colours)


@app.route("/results", methods=["GET"])
def results():
    title = 'Voting results'
    bar_labels = db.Votes.distinct("vote")
    bar_values = []
    for field in fields:
        bar_values.append(db["Votes"].find({"vote": field}).count())

    background_colors = possible_background_colors[:len(bar_labels)]
    border_colors = possible_border_colors[:len(bar_labels)]
    return render_template("results2.html", title=title,
                           labels=bar_labels, values=bar_values, colors=background_colors, borders=border_colors)


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
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(db, unique_id):
        User.create(db, unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    fields = db.Votes.distinct("vote")

    # print(field, num)
    app.run(ssl_context="adhoc", debug=True)
