from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

client = None
connected = False

def mongo_handler():
    global client, connected
    if connected:
        print("Disconnected from MongoDB.")
        client.close()
        client = None
        connected = False
    else:
        print("Attempting connection to MongoDB...")
        try:
            client = MongoClient(serverSelectionTimeoutMS=30) #may want to change timeout if not localhost
            client.server_info() #forces connection verification
            print("Connection Succeeded!")
            connected = True
        except (ConnectionFailure, KeyboardInterrupt) as e:
            print("Error: MongoDB not connected:", e)
        except Exception as e:
            print("Error:", e)

def get_dbnames():
    return client.database_names()

def get_collections(db_name):
    return client[db_name].collection_names()
