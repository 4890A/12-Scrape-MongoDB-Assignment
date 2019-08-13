from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

mongo = PyMongo(app, uri="mongodb://localhost:27017/mars")
mongo.db.mars_data.drop()

@app.route("/")
def home():
    mars_data = mongo.db.mars_data
    return render_template("index.html", mars_data =  mars_data.find_one())

@app.route("/scrape")
def scrape_button():
    mongo.db.mars_data.drop()
    results = scrape_mars.scrape()
    mars_data = mongo.db.mars_data
    mars_data.update({}, results, upsert=True)
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)
