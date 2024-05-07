from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from googleapiclient.discovery import build
import bson

app = Flask(__name__)


conn_string = "mongodb+srv://RicoRos85:C#ristina!23@40cluster0.obwdipy.mongodb.net"  # MongoDB Atlas connection string
client      = MongoClient(conn_string)                                              # Create a MongoDB client
db          = client['sample_mflix']                                                # Connect to a database
collection  = db['embedded_movies']                                                 # Access a collection

# Ensure the index exists each time the app starts
collection.create_index([("title", "text")])


def get_youtube_trailer_url(movie_title):
    youtube = build('youtube', 'v3', developerKey='AIzaSyD70N9aa6zSsm5Mm1HD6PMR2ygHuDvSWSU')
    request = youtube.search().list(
        q=f"{movie_title} official trailer",
        part="snippet",
        type="video",
        maxResults=1
    )
    response = request.execute()

    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        # Use the embed URL format
        return f"https://www.youtube.com/embed/{video_id}"
    return None



@app.route('/')
def index():
    genres = collection.distinct("genres")          # Retrieve genres from the 'genres' row in DB for the filter dropdown
    page = int(request.args.get('page', 1))         # Retrieve page number from query parameters
    limit = 25                                      # Number of movies per page
    skip = (page - 1) * limit                       # Calculate the number of movies to skip

    query_title = request.args.get('title', '')     # Retrieve query parameters
    query_genre = request.args.get('genre', '')     # Retrieve query parameters
    query_year  = request.args.get('year', '')      # Retrieve query parameters
    query_poster = request.args.get('poster', '')
    query_rating = request.args.get('rating', '')
    query_actor = request.args.get('actor', '')
    query_directors = request.args.get('directors', '')

    query = {}
    if query_title:
        query['title'] = {"$regex": query_title, "$options": "i"} # Case-insensitive search
    if query_genre:
        query['genres'] = query_genre
    if query_year:
        try:
            query['year'] = int(query_year)
        except ValueError:
            pass
    if query_rating:
        try:
            query['imdb.rating'] = {"$gte": float(query_rating)}
        except ValueError:
            pass # Ignore invalid rating values
    if query_actor:
        query['cast'] = query_actor
    if query_directors:
        query['directors'] = query_directors

     # Aggregation pipeline for fetching 25 random movies
    pipeline = [
        {"$match": query},              # Filtering based on query
        #{"$sort": {"year": -1}},        # Sort by year in descending order
        {"$skip": skip},                # Skip the documents for previous pages
        {"$limit": limit},              # Limit the results to 'limit' items
        {"$sample": {"size": 10000}}  # Use $sample to get random documents
    ]

    movies = list(collection.aggregate(pipeline))
    for movie in movies:
        if not movie.get('poster'):  # Check if 'poster' field is missing or empty
            movie['poster'] = 'https://www.prokerala.com/movies/assets/img/no-poster-available.jpg'  # Specify your default image path
  
    total_movies = collection.count_documents(query)
    total_pages = (total_movies + limit - 1) // limit # Calculate total pages needed
    return render_template('index.html', movies=movies, genres=genres,  page=page, total_pages=total_pages)


@app.route('/movie/<movie_id>')
def movie_detail(movie_id):
    movie = collection.find_one({'_id': bson.ObjectId(movie_id)})
    trailer_url = get_youtube_trailer_url(movie['title']) if movie else None
    return render_template('movie_detail.html', movie=movie, trailer_url=trailer_url)




if __name__ == '__main__':
    app.run(debug=True)
