# freedom-newsletter

Multi-agent AI-based weekly newsletter on the developments of freedom around the world. If you want to subscribe, email [bindi.federico@gmaill.com](mailto:bindi.federico@gmail.com).




database = client.get_database("sample_mflix")
result = database.cursor_command("find", "movies", filter={"runtime": 11})
print(result.to_list())


from pymongo import MongoClient
from bson.raw_bson import RawBSONDocument
from bson import CodecOptions
client: MongoClient = MongoClient()
options = CodecOptions(RawBSONDocument)
result = client.admin.command("ping", codec_options=options)
