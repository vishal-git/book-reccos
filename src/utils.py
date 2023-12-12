import os
import weaviate
from dotenv import load_dotenv

load_dotenv("./.env")


def get_client(openai=False):
    """
    Returns a Weaviate client with the correct authentification.
    """
    WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
    auth_config = weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)

    # if openai is True, the client will be configured to use the OpenAI API key
    if openai:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = weaviate.Client(
            url=WEAVIATE_URL,
            auth_client_secret=auth_config,
            additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
        )
    # otherwise, the client will be configured to use the Weaviate API key only
    else:
        client = weaviate.Client(url=WEAVIATE_URL, auth_client_secret=auth_config)

    return client
