import json
import sys

sys.path.append("..")


def vector_search(client, keyword):
    response = (
        client.query.get("Books", ["bookId", "title", "genres", "description"])
        .with_near_text({"concepts": [keyword]})
        .with_limit(3)
        .with_additional(["distance"])
        .do()
    )

    print(json.dumps(response, indent=4))

    resp_list = json.loads(json.dumps(response))["data"]["Get"]["Books"]

    try:
        for i, resp in enumerate(resp_list):
            print(
                f'{i}\nTitle: {resp["title"]}\nDescription: {resp["description"]}\nDistance: {resp["_additional"]["distance"]:.2f}\n'
            )
    except KeyError:
        print("No results found.")
        return None

    # filter out books with distance > .2
    resp_list = [resp for resp in resp_list if resp["_additional"]["distance"] <= 0.2]

    return resp_list


if __name__ == "__main__":
    from utils import get_client

    client = get_client(openai=True)

    vector_search(client, "science fiction")
