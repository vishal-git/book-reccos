import json
import sys

sys.path.append("..")
from utils import get_client

client = get_client()

response = (
    client.query.get("Books", ["title", "genres", "description"])
    .with_bm25(query="magic", properties=["description"])
    .with_additional("score")
    .with_limit(3)
    .do()
)

print(json.dumps(response, indent=2))
