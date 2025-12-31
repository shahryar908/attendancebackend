from pymongo import MongoClient

uri = "mongodb+srv://shahryar:qUTKMSlkk0Xuhlq0@cluster0.72le5.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)
db = client["test_db"]

print(db.list_collection_names())
Students=db['students']

student={
"name":"shahryar",
"age":22
}

Students.insert_one(student)
print("student inserted")

print(db.list_collection_names())
for s in Students.find():
    print(s)
