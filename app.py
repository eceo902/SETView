from flask import Flask, redirect, url_for, render_template, request, session, flash
from key import my_api_key
from newsapi import NewsApiClient
from datetime import timedelta

newsapi = NewsApiClient(api_key=my_api_key)


app = Flask(__name__)
app.secret_key = "secret_key"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/top")
def top():
    top_news = newsapi.get_top_headlines(q="technology OR entertainment OR sports", qintitle="technology OR entertainment OR sports", language="en", country="us", page_size=50)
    if(top_news["status"] != "ok"):
        flash("There was an error!, Try again")
        return render_template("trending.html")
    elif(top_news["totalResults"] == 0):
        flash("There are no articles right now.  Sorry, try again later!")
        return render_template("trending.html")
    else:
        articles = top_news["articles"]
        return render_template("trending.html", articles=articles)


@app.route("/all/<int:page_number>")
def all_things(page_number=None):
    all_news = newsapi.get_everything(q="technology OR entertainment OR sports", qintitle="technology OR entertainment OR sports", language="en", sort_by="relevancy", page_size=10, page=page_number)
    session["page"] = page_number
    if (all_news["status"] != "ok"):
        flash("There was an error!, Try again")
        return render_template("everything.html", current_page=1)
    elif (all_news["totalResults"] == 0):
        flash("There are no articles there right now.  Sorry, try again later!")
        return render_template("everything.html", current_page=1)
    elif(page_number == None):
        articles = all_news["articles"]
        return render_template("everything.html", articles=articles, current_page=1)
    else:
        articles = all_news["articles"]
        return render_template("everything.html", articles=articles, current_page=page_number)


@app.route("/<string:category>")
def cat(category):
    cat_news = newsapi.get_top_headlines(category=category.lower(), country="us", language="en", page_size=50)
    if (cat_news["status"] != "ok"):
        flash("There was an error!, Try again")
        return render_template("categories.html")
    elif (cat_news["totalResults"] == 0):
        flash("There are no articles right now.  Sorry, try again later!")
        return render_template("categories.html")
    else:
        articles = cat_news["articles"]
        return render_template("categories.html", articles=articles, type=category)



@app.route("/set", methods=["POST", "GET"])
def set_preferences():
    if request.method == "POST":
        pass
    else:
        return render_template("")


@app.route("/interests")
def interest():
    pass



@app.route("/check", methods=["POST", "GET"])
def search():
    pass


if __name__ == "__main__":
    app.run(debug=True)