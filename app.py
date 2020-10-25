from flask import Flask, redirect, url_for, render_template, request, session, flash
from key import Key
from newsapi import NewsApiClient
from datetime import timedelta

app = Flask(__name__)







if __name__ == "__main__":
    app.run(debug=True)