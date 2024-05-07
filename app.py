from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import bson

app = Flask(__name__)


conn_string = "mongodb+srv://RicoRos85:C#ristina!23@cluster0.obwdipy.mongodb.net/"  # MongoDB Atlas connection string
client      = MongoClient(conn_string)                                              # Create a MongoDB client
db          = client['sample_mflix']                                                # Connect to a database
collection  = db['embedded_movies']                                                 # Access a collection

# Ensure the index exists each time the app starts
collection.create_index([("title", "text")])


@app.route('/')
def index():
    genres = collection.distinct("genres")          # Retrieve genres from the 'genres' row in DB for the filter dropdown
    query_title = request.args.get('title', '')     # Retrieve query parameters
    query_genre = request.args.get('genre', '')     # Retrieve query parameters
    query_year  = request.args.get('year', '')      # Retrieve query parameters
    query_poster = request.args.get('poster', '')

    query = {}
    if query_title:
        query['title'] = {"$regex": query_title, "$options": "i"}
        movies = collection.find({"title": {"$regex": query_title, "$options": "i"}})
    else: 
        movies = collection.find().limit(50)
    if query_genre:
        query['genres'] = query_genre
    if query_year:
        query['year'] = int(query_year)
    if query_poster:
        query['poster'] = query_poster

    movies = collection.find(query)
    return render_template('index.html', movies=movies, genres=genres)


@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    movie = collection.find_one({'_id': bson.ObjectId(movie_id)})
    return render_template('movie_detail.html', movie=movie)

if __name__ == '__main__':
    app.run(debug=True)
