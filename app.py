from flask import Flask, redirect, url_for, render_template, request, session, flash
from key import my_api_key
from newsapi import NewsApiClient
from datetime import timedelta

newsapi = NewsApiClient(api_key=my_api_key)


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/top")
def top():
    top_news = newsapi.get_top_headlines(category="technology, sports, entertainment", country="us", language="en", page_size=50)
    if(top_news["status"] != "ok"):
        flash("There was an error!, Try again")
        return render_template("trending.html")
    elif(top_news["totalResults"] == 0):
        flash("There are no articles right now.  Sorry, try again later!")
        return render_template("trending.html")
    else:
        articles = top_news["articles"]
        return render_template("trending.html", articles=articles)


@app.route("/all")
def all():
    top_news = newsapi.get_everything()

@app.route("/<category>")
def cat(category):
    cat_news = newsapi.get_top_headlines(category=category, country="us", language="en", page_size=50)


if __name__ == "__main__":
    app.run(debug=True)