import sys

sys.path.append("../")
from utils import get_client

client = get_client(False)
print(client.schema.get())
