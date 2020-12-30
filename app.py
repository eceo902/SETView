from flask import Flask, redirect, url_for, render_template, request, session, flash
from key import my_api_key
from possible_preferences import technology_preferences, entertainment_preferences, sports_preferences
from newsapi import NewsApiClient               # newsapi object that works with the api
from datetime import timedelta, date
import random                                   # to randomize a list of articles for the carousel
import validators                               # to test if url is valid


newsapi = NewsApiClient(api_key=my_api_key)


app = Flask(__name__)                                                                           # creating the Flask App
app.secret_key = "secret_key"                                                                   # need to make a secret key to make session work
app.permanent_session_lifetime = timedelta(days=7)                                              # the session lasts for a week


@app.before_request                                                                             # this will run before any request
def make_session_permanent():
    session.permanent = True                                                                    # activates the session as being permanent

@app.before_first_request                                                                       # activates only before the first request
def set_initial_page():
    session["page"] = 1
    session["page_interest"] = 1
    session["categories"] = []                                                                  # sets session["categories"] to empty list

@app.route("/")                                                                                 # Homepage
def home():
    news = newsapi.get_everything(q="technology OR entertainment OR sports", qintitle="technology OR entertainment OR sports", language="en", sort_by="relevancy", page_size=100, from_param=date.today()-timedelta(days=2), to=date.today())
    articles = news["articles"]

    rtn = []

    for i in range(9):
        temp = random.choice(articles)                                                          # stores the random article in a temporary variable
        while temp["urlToImage"] is None or not validators.url(temp["urlToImage"]):             # if there is not a url or if the url is invalid
            articles.remove(temp)
            temp = random.choice(articles)
        rtn.append(temp)                                                                        # adds the random article to the return list
        articles.remove(temp)                                                                   # removes the random article from the list of articles

    for article in rtn:                                                                         # limiting the length of the title
        if len(article["title"]) > 90:
            article["title"] = article["title"][0:article["title"].find(" ", 85)] + "..."       # this will add an ellipsis to the first space it finds starting from the 70th character

    return render_template("home.html", rtn=rtn)



@app.route("/top")                                                                              # trending sports, technology, and entertainment news page
def top():
    top_technology = newsapi.get_top_headlines(category="technology", country="us", page_size=34)                       # calling the api for tech news
    top_entertainment = newsapi.get_top_headlines(category="entertainment", country="us", page_size=33)                 # calling the api for entertainment news
    top_sports = newsapi.get_top_headlines(category="sports", country="us", page_size=33)                               # calling the api for sports news
    if top_technology["status"] != "ok" or top_entertainment["status"] != "ok" or top_sports["status"] != "ok":         # will flash an error if the status is not ok
        flash("There was an error!, Try again")
        return redirect(url_for("home"))
    elif top_technology["totalResults"] == 0 and top_entertainment["totalResults"] == 0 and top_sports["totalResults"] == 0:   # will flash an error if there are no results
        flash("There are no articles right now.  Sorry, try again later!")
        return redirect(url_for("home"))
    else:
        articles = top_technology["articles"] + top_entertainment["articles"] + top_sports["articles"]                  # adding the different categories together
        random.shuffle(articles)                                                                                        # randomizing the order of the categories
        return render_template("trending.html", articles=articles)


@app.route("/all/<int:page_number>")                                                            # all technology, sports, and entertainment news
def all_things(page_number=1):
    all_news = newsapi.get_everything(q="technology OR entertainment OR sports", qintitle="technology OR entertainment OR sports", language="en", sort_by="relevancy", page_size=20, page=page_number, from_param=date.today()-timedelta(days=7), to=date.today())
    session["page"] = page_number                                                               # saves the page_number into a "page" input in the session
    if all_news["status"] != "ok":
        flash("There was an error!, Try again")
        return redirect(url_for("home"))
    elif all_news["totalResults"] == 0:
        flash("There are no articles there right now.  Sorry, try again later!")
        return redirect(url_for("all_things", page_number=session["page"]-1))                   # going back to previous page
    else:
        articles = all_news["articles"]
        return render_template("everything.html", articles=articles, current_page=page_number)


@app.route("/category/<string:category>")                                                       # News from either technology, entertainment, or sports category
def cat(category):
    cat_news = newsapi.get_top_headlines(category=category.lower(), country="us", language="en", page_size=50)
    if cat_news["status"] != "ok":
        flash("There was an error!, Try again")
        return redirect(url_for("home"))
    elif cat_news["totalResults"] == 0:
        flash("There are no articles right now.  Sorry, try again later!")
        return redirect(url_for("home"))
    else:
        articles = cat_news["articles"]
        return render_template("categories.html", articles=articles, type=category)






@app.route("/set", methods=["POST", "GET"])
def set_preferences():
    if request.method == "POST":
        try:
            session["preferences"] = request.form.getlist("list")                               # getting the list of checked values for the checkboxes
            if len(request.form.getlist("list")) > 0:
                flash("Your interests have been saved!")
            return redirect(url_for("interest", page_number=1))                                 # if preferences were selected, then go to interest function
        except:
            flash("Please select some preferences")
            return redirect(url_for("set_preferences"))
    else:
        return render_template("list_of_preferences.html", technology_preferences=technology_preferences, entertainment_preferences=entertainment_preferences, sports_preferences=sports_preferences)


@app.route("/interests/<int:page_number>")
def interest(page_number=1):
    if "preferences" in session and len(session["preferences"]) > 0:                            # if there are saved preferences in the session
        preferences = " OR ".join(session["preferences"])
        interest_news = newsapi.get_everything(q=preferences.lower(), qintitle=preferences.lower(), language="en", page_size=20, page=page_number)
        session["page_interest"] = page_number
        if interest_news["status"] != "ok":
            session.pop("_flashes", None)                                                       # removing the previous flashes
            flash("There was an error!, Try again")
            return redirect(url_for("home"))
        elif interest_news["totalResults"] == 0:
            session.pop("_flashes", None)
            flash("There are no articles there right now.  Sorry, try again later!")
            return redirect(url_for("home"))
        else:
            articles = interest_news["articles"]
            return render_template("interest_page.html", articles=articles, current_page=page_number)
    else:
        flash("You need to set preferences first!")
        return redirect(url_for("set_preferences"))






@app.route("/checktype", methods=["POST", "GET"])                                               # checking to see if the input search for type was valid
def try_type():
    if request.method == "POST":
        topic = request.form["what"]
        if topic is not None and len(topic) > 0:                                                # if something was entered in the search
            session["categories"] = request.form.getlist("categories")
            return redirect(url_for("topic_searcher", topic=topic, page_number=1))
        else:
            flash("Invalid search input, try again!")
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))


@app.route("/topic/<string:topic>/<int:page_number>")                                           # route to render the search result
def topic_searcher(topic, page_number=1):
    if session["categories"] is None or len(session["categories"]) == 0:
        try:
            news_by_topic = newsapi.get_everything(q="(technology OR entertainment OR sports) AND " + topic.lower(), language="en", sort_by="relevancy", page_size=20, page=page_number)
        except:
            flash("here was an error with your search.")
            return redirect(url_for("home"))
    else:
        try:
            narrow_search = " OR ".join(session["categories"])
            news_by_topic = newsapi.get_everything(q="(" + narrow_search.lower() + ") AND " + topic.lower(), language="en", sort_by="relevancy", page_size=20, page=page_number)
        except:
            flash("There was an error with your search.")
            return redirect(url_for("home"))

    if news_by_topic["status"] != "ok":
        flash("There was an error with your search.")
        return redirect(url_for("home"))
    elif news_by_topic["totalResults"] == 0:
        flash("Sorry, there are no results for this search, try something else!")
        return redirect(url_for("home"))
    else:
        articles = news_by_topic["articles"]
        return render_template("topic.html", articles=articles, topic=topic, current_page=page_number)






@app.route("/checksource", methods=["POST", "GET"])                                             # checking if the input for the search is valid
def try_source():
    if request.method == "POST":
        source = request.form["what"]
        if source is not None and len(source) > 0:                                              # if there was actual text that was searched
            session["categories"] = request.form.getlist("categories")
            return redirect(url_for("source_searcher", source=source, page_number=1))
        else:
            flash("Invalid search input, try these sources!")
            return redirect(url_for("source_list"))
    else:
        return redirect(url_for("home"))


@app.route("/source/<string:source>/<int:page_number>")
def source_searcher(source, page_number=1):
    if "categories" not in session or len(session["categories"]) == 0:                        # if there are "categories" saved in the session
        try:
            news_by_source = newsapi.get_everything(q="technology OR entertainment OR sports", language="en", sort_by="relevancy", sources=source.lower(), page_size=20, page=page_number)
        except:
            flash("There was an error with your search.  Try these!")
            return redirect(url_for("source_list"))
    else:
        try:
            narrow_search = " OR ".join(session["categories"])
            news_by_source = newsapi.get_everything(q=narrow_search, language="en", sort_by="relevancy", sources=source.lower(), page_size=20, page=page_number)
        except:
            flash("There was an error with your search.  Try these!")
            return redirect(url_for("source_list"))
    if news_by_source["status"] != "ok":
        flash("There was an error with your search.  Try these!")
        return redirect(url_for("source_list"))
    elif news_by_source["totalResults"] == 0:
        flash("Sorry, there are no results for this search, try these!")
        return redirect(url_for("source_list"))
    else:
        articles = news_by_source["articles"]
        return render_template("source.html", articles=articles, source=source, current_page=page_number)


@app.route("/sourcelist")
def source_list():
    session["categories"] = []                                                                                  # setting to an empty list
    technology_sources = newsapi.get_sources(category="technology", language="en", country="us")                # gets the news sources that deal with technology
    entertainment_sources = newsapi.get_sources(category="entertainment", language="en", country="us")          # gets the news sources that deal with entertainment
    sports_sources = newsapi.get_sources(category="sports", language="en", country="us")                        # gets the news sources that deal with sports

    combined = technology_sources["sources"] + entertainment_sources["sources"] + sports_sources["sources"]     # combining the different sources of news

    return render_template("list_of_sources.html", sources=combined)



@app.route("/eseeyave")                                                                         # rendering the about page
def creator():
    return render_template("about.html")



if __name__ == "__main__":
    app.run(debug=True)                                                                         # changes to code will change app