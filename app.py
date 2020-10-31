from flask import Flask, redirect, url_for, render_template, request, session, flash
from key import my_api_key
from newsapi import NewsApiClient
from datetime import timedelta, date
import random                           # to randomize a list of articles for the carousel
import validators                       # to test if url is valid

newsapi = NewsApiClient(api_key=my_api_key)


app = Flask(__name__)
app.secret_key = "secret_key"


@app.route("/")                         # Homepage
def home():
    news = newsapi.get_everything(q="technology OR entertainment OR sports", qintitle="technology OR entertainment OR sports", language="en", sort_by="relevancy", page_size=100, from_param=date.today()-timedelta(days=2), to=date.today())
    articles = news["articles"]

    rtn = []

    for i in range(9):
        temp = random.choice(articles)          # stores the random article in a temporary variable
        while temp["urlToImage"] is None or not validators.url(temp["urlToImage"]):            # if there is not a url or if the url is invalid
            articles.remove(temp)
            temp = random.choice(articles)
        rtn.append(temp)                        # adds the random article to the return list
        articles.remove(temp)                   # removes the random article from the list of articles

    for article in rtn:                         # limiting the length of the title
        if len(article["title"]) > 75:
            article["title"] = article["title"][0:article["title"].find(" ", 70)] + "..."       # this will add an ellipsis to the first space it finds starting from the 70th character

    return render_template("home.html", rtn=rtn)


@app.route("/top")                      # Trending sports, technology, and entertainment news page
def top():
    top_technology = newsapi.get_top_headlines(category="technology", country="us", page_size=34)
    top_entertainment = newsapi.get_top_headlines(category="entertainment", country="us", page_size=33)
    top_sports = newsapi.get_top_headlines(category="sports", country="us", page_size=33)
    if(top_technology["status"] != "ok" or top_entertainment["status"] != "ok" or top_sports["status"] != "ok"):        # will flash an error if the status is not ok
        flash("There was an error!, Try again")
        return redirect(url_for("home"))
    elif(top_technology["totalResults"] == 0 and top_entertainment["totalResults"] == 0 and top_sports["totalResults"] == 0):   # Will flash an error if there are no results
        flash("There are no articles right now.  Sorry, try again later!")
        return redirect(url_for("home"))
    else:
        articles = top_technology["articles"] + top_entertainment["articles"] + top_sports["articles"]                  # adding the different categories together
        random.shuffle(articles)                                                                                        # randomizing the order of the categories
        return render_template("trending.html", articles=articles)


@app.route("/all/<int:page_number>")    # All technology, sports, and entertainment news
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


@app.route("/category/<string:category>")        # News from either technology, entertainment, or sports category
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






@app.route("/checktype", methods=["POST", "GET"])                                       # checking to see if the input search for type was valid
def try_type():
    if request.method == "POST":
        if request.form["what_topic"] is not None and len(request.form["what_topic"]) > 0:
            return redirect(url_for("topic_searcher", topic=request.form["what_topic"]))
        else:
            flash("Invalid search input, try again!")
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


@app.route("/topic/<string:topic>")                                                     # route to render the search result
def topic_searcher(topic):
    news_by_topic = newsapi.get_everything(q="(technology OR entertainment OR sports) AND " + topic.lower(), language="en", sort_by="relevancy", page_size=100)
    if news_by_topic["status"] != "ok":
        flash("There was an error with your search.")
        return redirect(url_for("home"))
    elif news_by_topic["totalResults"] == 0:
        flash("Sorry, there are no results for this search, try something else!")
        return redirect(url_for("home"))
    else:
        articles = news_by_topic["articles"]
        return render_template("topic.html", articles=articles)




@app.route("/checksource", methods=["POST", "GET"])
def try_source():
    if request.method == "POST":
        if request.form["what_source"] is not None and len(request.form["what_source"]) > 0:
            return redirect(url_for("source_searcher", source=request.form["what_source"]))
        else:
            flash("Invalid search input, try again!")
            return redirect(url_for("source_list"))
    else:
        return redirect(url_for("home"))


@app.route("/source/<string:source>")
def source_searcher(source):
    try:
        news_by_source = newsapi.get_everything(q="technology OR entertainment OR sports", language="en", sort_by="relevancy", sources=source.lower(), page_size=100)
    except:
        flash("There was an error with your search.")
        return redirect(url_for("source_list"))
    if news_by_source["status"] != "ok":
        flash("There was an error with your search.")
        return redirect(url_for("source_list"))
    elif news_by_source["totalResults"] == 0:
        flash("Sorry, there are no results for this search, try something else!")
        return redirect(url_for("source_list"))
    else:
        articles = news_by_source["articles"]
        return render_template("source.html", articles=articles)


@app.route("/sourcelist")
def source_list():
    technology_sources = newsapi.get_sources(category="technology", language="en", country="us")
    entertainment_sources = newsapi.get_sources(category="entertainment", language="en", country="us")
    sports_sources = newsapi.get_sources(category="sports", language="en", country="us")

    combined = technology_sources["sources"] + entertainment_sources["sources"] + sports_sources["sources"]     # combining the different sources of news

    return render_template("list_of_sources.html", sources=combined)





@app.route("/test")
def test():
    news = newsapi.get_everything(q="tnf",
                                  qintitle="tnf", language="en", sort_by="relevancy",
                                  page_size=100, from_param=date.today() - timedelta(days=3), to=date.today())

    articles = news['articles']


    return render_template("test.html", articles=articles, check=type(validators.url(articles[0]["urlToImage"])))


if __name__ == "__main__":
    app.run(debug=True)