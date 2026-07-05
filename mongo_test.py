from time_objects import ts

with open('output_4.md', 'r', encoding="utf-8") as f:
    text = f.read()

import dotenv
dotenv.load_dotenv()
import os

db_password = os.environ["MONGO_PASSWORD"]

conn_string = f'mongodb+srv://bindifederico_db_user:{db_password}@cluster0.nndb8ya.mongodb.net/?appName=Cluster0&compressors=zlib'

from pymongo import MongoClient
client: MongoClient = MongoClient(conn_string)


database = client.get_database("nika-newsletter")
collection = database['newsletter-texts']

data = {
    'ts':ts,
    'text':text
}

result = collection.insert_one(data)
result = database.cursor_command("find", "newsletter-texts")
print(result.to_list())