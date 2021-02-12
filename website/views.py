import string
import random
# Third-party libraries
from flask import Blueprint, redirect, request, url_for, render_template, flash
from flask_login import (
    current_user,
)
from .models import Vote
from .config.table_config import *
from . import db

views = Blueprint("views", __name__)



def id_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@views.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == "POST":
                other_questions = db["Info"].find()
                q = request.form["question"]
                if q == "":
                    flash("Question can not be empty", category="danger")
                    return render_template("admin_add.html")

                for quer in other_questions:
                    if "".join(q.split(" ")).lower() == "".join(quer["title"].split(" ")).lower():
                        flash("Similar question already exists", category="danger")
                        return render_template("admin_add.html")

                ans = []
                for a in request.form.getlist('answer'):
                    if a != "":
                        ans.append(a.strip())
                if len(ans) < 2:
                    flash("U need more answers", category="danger")
                    return render_template("admin_add.html")

                if len(ans) > 20:
                    flash("Too many answers max is 20", category="danger")
                    return render_template("admin_add.html")

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
                    cluster_insert = db["Info"].insert(query, check_keys=False)
                    flash("Question added", category="info")
                    return render_template("admin_add.html")
            return render_template("admin_add.html")

        else:
            flash("You are not an admin", category="danger")
            return redirect(url_for("auth.index"))
    else:
        return redirect(url_for("auth.login"))


@views.route("/admin/delete", methods=["GET", "POST"])
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
                return redirect(url_for("views.admin_delete"))
            return render_template("admin_delete.html", vote_labels=vote_labels)
        else:
            flash("You are not an admin", category="danger")
            return redirect(url_for("views.index"))
    else:
        return redirect(url_for("auth.login"))


@views.route("/")
def index():
    return render_template("home.html")


@views.route("/vote")
def vote():
    vote_labels = list(db["Info"].distinct("voting_id"))
    if len(vote_labels) == 0:
        flash("There are no votings to show", category="danger")
        return redirect(url_for("views.index"))
    return redirect(url_for("views.voteparam", voting_id=vote_labels[0]))


@views.route("/vote/<voting_id>", methods=["GET", "POST"])
def voteparam(voting_id):
    vote_labels = []
    query = db["Info"].find()
    for col in query:
        vote_labels.append([col["voting_id"], col["title"]])

    voting_data = db["Info"].find_one({"voting_id": voting_id})
    q = voting_data["title"]
    ans = voting_data["ans"].items()

    if current_user.is_authenticated:
        if request.method == "POST":
            checboxes_votes = [val for val in request.form]
            if len(checboxes_votes) == 0:
                flash('Vote can not be empty', category="danger")
                return render_template("vote.html", question=q, ans=ans, vote_labels=vote_labels)

            if len(checboxes_votes) > 1:
                flash('Too many args', category="danger")
                return render_template("vote.html", question=q, ans=ans, vote_labels=vote_labels)

            else:
                voters_id = current_user.id
                if Vote.vote_exists(db, voters_id, voting_id):
                    flash('You can not vote more than once', category="danger")
                    return render_template("vote.html", question=q, ans=ans,
                                           vote_labels=vote_labels)
                else:
                    vote_id = str(checboxes_votes[0])
                    swapped = {value: key for key, value in voting_data["ans"].items()}
                    vote = swapped[vote_id]
                    Vote.create(db, voters_id, vote, voting_id)
                    return redirect(url_for("views.resultsparam", voting_id=voting_id))
    else:
        return redirect(url_for("auth.login"))

    return render_template("vote.html", question=q, ans=ans, vote_labels=vote_labels)


@views.route("/results")
def results():
    vote_labels = list(db["Info"].distinct("voting_id"))
    if len(vote_labels) == 0:
        flash("There are no results to show", category="danger")
        return redirect(url_for("views.index"))
    return redirect(url_for("views.resultsparam", voting_id=vote_labels[0]))


@views.route("/results/<voting_id>")
def resultsparam(voting_id):
    vote_labels = []
    query = db["Info"].find()
    for col in query:
        vote_labels.append([col["voting_id"], col["title"]])

    # get vote info
    voting_data = db["Info"].find_one({"voting_id": voting_id})
    title = voting_data["title"]
    bar_labels = voting_data["ans"].keys()

    bar_values = []
    for field in bar_labels:
        count = db[voting_id].count_documents({"vote": field})
        bar_values.append(count)

    background_colors = possible_background_colors[:len(bar_labels)]
    border_colors = possible_border_colors[:len(bar_labels)]
    return render_template("results.html", title=title,
                           labels=bar_labels, values=bar_values, colors=background_colors, borders=border_colors,
                           vote_labels=vote_labels)
