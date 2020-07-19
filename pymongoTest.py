#pip install pymongo
#Don't name this file pymongo.py
#DNS Seedlist Connection Format 

from pymongo import MongoClient
import urllib 
import pprint

username = "petebchamp"
password = urllib.parse.quote("<Password>")
cluster = "petemongocluster-zz9io.gcp.mongodb.net"
database_name = "sample_mflix"
collection_name = "movies"


mongo_uri = "mongodb+srv://" + username + ":" + password + "@" + cluster + "/test"
client = MongoClient(mongo_uri)
db = client[database_name]
coll = db[collection_name]

for x in coll.find({},{ "_id": 0, "title": 1, "year": 1 }).limit(5):
    print(x)

myquery = { "title": "Diner" }

for x in coll.find(myquery):
    pprint.pprint(x)

pipeline = [
#    {
#        '$group': {
#            '_id': {"rated": "$rated"},
#            'count': {'$sum': 1}
#                
#        },
#    },
#    {
#         '$sort': {'count': -1}
#     
#    }
    {
         '$sortByCount': "$rated" #Same as above
     }
]

print(list(coll.aggregate(pipeline)))
