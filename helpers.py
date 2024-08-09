import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import geocoder
from geopy.geocoders import Nominatim
from cs50 import SQL

from flask import redirect, render_template, session
from functools import wraps

db = SQL("sqlite:///blog.db")

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    # Define @login_required
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def location():
    """Look up for user's current location."""

    geo = geocoder.ip('me')
    return geo.latlng


def delete_blog(blog_id):
    return db.execute("DELETE FROM blog WHERE blog_id = ?", blog_id)
