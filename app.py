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
    top_news = newsapi.get_top_headlines(category="technology")


@app.route("/all")
def all():
    top_news = newsapi.get_everything()



if __name__ == "__main__":
    app.run(debug=True)