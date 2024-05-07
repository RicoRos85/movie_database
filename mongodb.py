from pymongo import MongoClient

# MongoDB Atlas connection string
conn_string = "mongodb+srv://RicoRos85:C#ristina!23@cluster0.obwdipy.mongodb.net/"

# Create a MongoDB client
client = MongoClient(conn_string)

# Connect to a database
db = client['sample_mflix']

# Access a collection
collection = db['embedded_movies']

all_documents = collection.find({}, {'title': 1, '_id': 0})


for document in all_documents:
    print(document)