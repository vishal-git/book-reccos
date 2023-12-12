import pandas as pd
import weaviate
import os
from dotenv import load_dotenv

load_dotenv("./.env")

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

auth_config = weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)

# TODO: Replace this with get_client()
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=auth_config,
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

# load data
df = pd.read_csv(
    "./data/books.csv", usecols=["bookId", "title", "description", "genres", "coverImg"]
)

# if the Books schema already exists, delete it
current_schema = client.schema.get()["classes"]
for schema in current_schema:
    if schema["class"] == "Books":
        client.schema.delete_class("Books")

# create the Books schema
books_schema = {
    "class": "Books",
    "description": "A collection of book titles and descriptions",
    "vectorizer": "text2vec-openai",
    "vectorIndexConfig": {
        "distance": "cosine",
    },
    "moduleConfig": {
        "text2vec-openai": {
            "vectorizeClassName": False,
            "model": "ada",
            "modelVersion": "002",
            "type": "text",
        },
    },
}

books_schema["properties"] = [
    {
        "name": "bookId",
        "dataType": ["string"],
        "description": "The id of the book",
        "moduleConfig": {
            "text2vec-openai": {
                "skip": True,
                "vectorizePropertyName": False,
            },
        },
    },
    {
        "name": "title",
        "dataType": ["string"],
        "description": "The title of the book",
        "moduleConfig": {
            "text2vec-openai": {
                "skip": True,
                "vectorizePropertyName": False,
            },
        },
    },
    {
        "name": "description",
        "dataType": ["text"],
        "description": "The description of the book",
    },
    {
        "name": "genres",
        "dataType": ["text"],
        "description": "The genre of the book",
    },
]

client.schema.create_class(books_schema)

# configure batch process
client.batch.configure(
    batch_size=50,
    dynamic=True,
    timeout_retries=3,
)

for i in range(len(df)):
    item = df.iloc[i]

    book_object = {
        "bookId": item["bookId"],
        "title": item["title"],
        "description": item["description"],
        "genres": item["genres"],
    }

    try:
        client.batch.add_data_object(book_object, "Books")
    except BaseException as error:
        print(f"Import failed at {i}")
        print(item)
        print(f"An exception occurred: {error}")
        pass

print(client.query.aggregate("Books").with_meta_count().do())
# client.batch.flush()
